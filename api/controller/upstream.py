from datetime import datetime
import random
from flask import request
from flask_restful import Resource
from util import db
from model.hotspot import hotspot
from model.rxpk import rxpk
from model.txpk import txpk
from helium.radio import decrypt_radio, fspl, freq_channel
from auth import authorize_hotspot
from sqlalchemy import exc, exists
import json
import math

class upstream(Resource):
    @authorize_hotspot
    def get(self, hotspot_address):
        requester = hotspot.query.filter_by(address=hotspot_address).first()

        rxpk_q = rxpk.query\
            .filter(rxpk.group_id==requester.group_id)\
            .filter(rxpk.receiver_address!=hotspot_address)\
            .filter(rxpk.received_time > requester.last_pocs_sent)\
            .filter(~exists().where(txpk.poc_id == rxpk.poc_id))\
            .order_by(rxpk.received_time)
            
        rxpk_list = []
        for rxpk_item in rxpk_q:
            push_data_msg = json.loads(rxpk_item.payload)
            # reverse path loss to approximate signal distance to receiver hotspot
            d_tx_to_rx = 10 ** ((push_data_msg["rssi"] * -1 + 147.55 + rxpk_item.receiver_gain / 10) / 20) / (push_data_msg["freq"] * 10**6)
            path_loss = fspl(
                rxpk_item.receiver_lat,
                rxpk_item.receiver_lng,
                requester.lat,
                requester.lng,
                push_data_msg["freq"] * 10 ** 6,
                requester.gain / 10,
                d_tx_to_rx
            )
            path_loss += random.randint(-30, -1)
            path_loss = int(path_loss)
            push_data_msg["rssi"] = path_loss
            push_data_msg["rssis"] = path_loss
            push_data_msg["rssic"] = path_loss

            # calculate noise floor to calculate snr
            noise_floor_theoretical = int(-174 + math.log10(125 * 1000) * 10) * -1 # 125kHz bandwidth, room temperature
            noise_floor = random.randint(noise_floor_theoretical - 20, noise_floor_theoretical) + round(random.random(), 2) * -1
            snr = path_loss - noise_floor
            if snr < -19: # skip if snr below -20dbm (cannot be decoded)
                continue

            push_data_msg["lsnr"] = snr

            rxpk_list.append(push_data_msg)

        txpk_q = txpk.query\
            .filter(txpk.group_id==requester.group_id)\
            .filter(txpk.transmitted_time > requester.last_pocs_sent)\
            .order_by(txpk.transmitted_time)
        
        for txpk_item in txpk_q:
            pull_data_msg = json.loads(txpk_item.payload)
            path_loss = fspl(
                txpk_item.transmitter_lat,
                txpk_item.transmitter_lng,
                requester.lat,
                requester.lng,
                pull_data_msg["freq"] * 10 ** 6,
                requester.gain / 10
            )
            path_loss += random.randint(-30, -1)
            path_loss = int(path_loss)

            # calculate noise floor to calculate snr
            noise_floor_theoretical = int(-174 + math.log10(125 * 1000) * 10) * -1 # 125kHz bandwidth, room temperature
            noise_floor = random.randint(noise_floor_theoretical - 20, noise_floor_theoretical) + round(random.random(), 2) * -1
            snr = path_loss - noise_floor
            if snr < -19: # skip if snr below -20dbm (cannot be decoded)
                continue
            
            # format to rxpk format
            tx_to_rx = {
                "tmst": pull_data_msg["tmst"],
                "freq": pull_data_msg["freq"],
                "chan": freq_channel(pull_data_msg["freq"]),
                "rfch": pull_data_msg["rfch"],
                "stat": 1,
                "modu": pull_data_msg["modu"],
                "datr": pull_data_msg["datr"],
                "codr": pull_data_msg["codr"],
                "rssi": path_loss,
                "rssis": path_loss,
                "rssic": path_loss,
                "lsnr": snr,
                "size": pull_data_msg["size"],
                "data": pull_data_msg["data"],
            }
            rxpk_list.append(tx_to_rx)

        requester.last_pocs_sent = datetime.utcnow()
        db.session.commit()
        return {"rxpk":rxpk_list}, 200
    
    @authorize_hotspot
    def post(self, hotspot_address):
        push_data_msg = request.get_json()

        msg = decrypt_radio(push_data_msg["data"])
        if msg is None or msg.header.oui != 0 or msg.header.did != 1:
            return {'message' : 'not helium PoC'}, 400
        
        try:
            receiver = hotspot.query.filter_by(address=hotspot_address).first()
            new_rxpk = rxpk(
                group_id=receiver.group_id, 
                poc_id=msg.poc_id, 
                payload=json.dumps(push_data_msg), 
                receiver_lat=receiver.lat, 
                receiver_lng=receiver.lng, 
                receiver_address=hotspot_address, 
                receiver_gain=receiver.gain)
            db.session.add(new_rxpk)
            db.session.commit()
            return {'message' : 'PoC succesfuly pushed'}, 200
        except exc.IntegrityError:
            db.session.rollback()
            return {'message' : 'PoC already pushed by another hotspot'}, 200
