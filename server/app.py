from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  


class SmartCart:
    sensor_names = ["Barcode", "charachteristic", "RFID tag", "Help button"]

    def __init__(self, sensors):
        self.sensors = sensors  

    def multiplex(self, s1, s0):
        sel = (s1 << 1) | s0
        return sel, self.sensors[sel]


class SupermarketServer:
    system_names = ["Billing System", "Security System",
                    "Inventory Database", "Customer Service Desk"]

    def demultiplex(self, signal, s1, s0):
        sel = (s1 << 1) | s0
        outputs = ["Idle - No Data"] * 4
        outputs[sel] = signal
        return sel, self.system_names[sel], outputs


@app.get("/")
def index():
    return "Smart Cart backend is running"


@app.get("/api/data")      
def data():
    return jsonify(message="Hello from Flask backend!")


@app.post("/api/transmit")
def transmit():
    body = request.get_json(silent=True) or {}
    sel = body.get("sel")
    sensors = body.get("sensors")

    if (not isinstance(sel, int) or not 0 <= sel <= 3
            or not isinstance(sensors, list) or len(sensors) != 4):
        return jsonify(error="sel must be 0-3 and sensors a list of 4"), 400

    sensors = [str(s)[:40] or "No data" for s in sensors]
    s1, s0 = (sel >> 1) & 1, sel & 1

    cart = SmartCart(sensors)
    server = SupermarketServer()

    mux_sel, line = cart.multiplex(s1, s0)                     
    dmx_sel, dest, outputs = server.demultiplex(line, s1, s0)  

    return jsonify(sel=mux_sel, s1=s1, s0=s0, line=line,
                   sensor=SmartCart.sensor_names[mux_sel],
                   dest=dest, outputs=outputs)


if __name__ == "__main__":  
    app.run(host="127.0.0.1", port=5000, debug=True)
