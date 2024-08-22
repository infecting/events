import grpc
from concurrent import futures
import time
import sensor_pb2
import sensor_pb2_grpc
import numpy as np
import scipy.special
import traceback
from config import Config
from controller import Controller
from synthesizer import Synthesizer


class SensorService(sensor_pb2_grpc.SensorServiceServicer):
    def GenerateSensorData(self, request, context):
        try:
            # Extracting parameters from the gRPC request
            duration = request.duration if request.duration else 1.2
            x0 = request.x0 if request.x0 else 308
            y0 = request.y0 if request.y0 else np.random.uniform()
            complexity = request.complexity if request.complexity else 2
            xf = list(request.xf) if request.xf else None
            yf = list(request.yf) if request.yf else None
            signature = request.signature
            # signature = request.signature
            print(request)
            if signature != "069137edba02f36dee55059df92cb06de45ce2a5":
                return sensor_pb2.SensorResponse(
                    error=str(
                        "dont try that here lol. logged your request and haxxing ip"),
                    traceback=traceback.format_exc(),
                    controller_dump="j"
                )

            # Initialize configuration and controller
            config = Config(duration=duration, x0=x0, y0=y0,
                            complexity=complexity, xf=xf, yf=yf)
            controller = Controller(config, None, None, None, None, None)
            synthesizer = Synthesizer(config, controller)

            # Generate mouse data
            t, x, y, v = synthesizer.generate_mouse_data()
            sensor_data = synthesizer.format_mouse_data(x, y, t)

            return sensor_pb2.SensorResponse(sensor_data=sensor_data)

        except Exception as e:
            print(f"Error occurred during sensor data generation: {e}")
            if controller:
                error_dump = controller.dump()
            else:
                error_dump = "Controller not initialized"
            print(traceback.format_exc())
            return sensor_pb2.SensorResponse(
                error=str(e),
                traceback=traceback.format_exc(),
                controller_dump=error_dump
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sensor_pb2_grpc.add_SensorServiceServicer_to_server(
        SensorService(), server)
    # This is where the server listens for requests
    server.add_insecure_port('[::]:5400')
    server.start()
    print("gRPC server started on port 5400...")
    try:
        while True:
            time.sleep(86400)  # Keep the server running
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
