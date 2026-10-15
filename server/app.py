from flask import Flask, request, jsonify, send_from_directory


app = Flask(__name__, static_folder=None)



class SmartCart:
    """Cart side: 4:1 MULTIPLEXER."""
    sensor_names = ["Barcode", "charachteristic", "RFID tag", "Help button"]

    def __init__(self, sensors):
        self.sensors = sensors  # D0..D3

    def multiplex(self, s1, s0):
        sel = (s1 << 1) | s0
        return sel, self.sensors[sel]


class SupermarketServer:
    """Server side: 1:4 DEMULTIPLEXER."""
    system_names = ["Billing System", "Security System",
                    "Inventory Database", "Customer Service Desk"]

    def demultiplex(self, signal, s1, s0):
        sel = (s1 << 1) | s0
        outputs = ["Idle - No Data"] * 4
        outputs[sel] = signal
        return sel, self.system_names[sel], outputs


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.post("/api/transmit")
def transmit():
    data = request.get_json(silent=True) or {}
    sel = data.get("sel")
    sensors = data.get("sensors")

    if (not isinstance(sel, int) or not 0 <= sel <= 3
            or not isinstance(sensors, list) or len(sensors) != 4):
        return jsonify(error="sel must be 0-3 and sensors a list of 4"), 400

    sensors = [str(s)[:40] or "No data" for s in sensors]
    s1, s0 = (sel >> 1) & 1, sel & 1

    cart = SmartCart(sensors)
    server = SupermarketServer()

    mux_sel, line = cart.multiplex(s1, s0)            # MUX
    dmx_sel, dest, outputs = server.demultiplex(line, s1, s0)  # DEMUX

    app.logger.info("S1S0=%d%d  D%d '%s' -> Y%d %s",
                    s1, s0, mux_sel, line, dmx_sel, dest)
    return jsonify(sel=mux_sel, s1=s1, s0=s0, line=line,
                   sensor=SmartCart.sensor_names[mux_sel],
                   dest=dest, outputs=outputs)


if __name__ == "__main__":
    print("Open http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
