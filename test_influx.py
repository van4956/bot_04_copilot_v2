# from influxdb_client import InfluxDBClient, Point # type: ignore
# from influxdb_client.client.write_api import SYNCHRONOUS
# import os
# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()

# # Параметры подключения
# print("Параметры подключения:")
# print(f"URL: http://localhost:8086")
# print(f"Token: {os.getenv('INFLUXDB_TOKEN')}")
# print(f"Org: {os.getenv('INFLUXDB_ORG')}")
# print(f"Bucket: {os.getenv('INFLUXDB_BUCKET')}")
# print("-" * 50)

# client = InfluxDBClient(
#     url="http://localhost:8086",
#     token=os.getenv('INFLUXDB_TOKEN'), # type: ignore
#     org=os.getenv('INFLUXDB_ORG') # type: ignore
# )

# try:
#     # Проверка подключения
#     health = client.health()
#     print(f"InfluxDB Status: {health.status}")

#     # Запись тестовых данных
#     write_api = client.write_api(write_options=SYNCHRONOUS)

#     point = Point("test_measurement") \
#         .tag("test_tag", "test1") \
#         .field("value", 25.0) \
#         .time(datetime.utcnow())

#     write_api.write(bucket=os.getenv('INFLUXDB_BUCKET'), record=point) # type: ignore
#     print("Тестовые данные записаны")

#     # Чтение данных
#     query = f'''
#     from(bucket:"{os.getenv('INFLUXDB_BUCKET')}")
#         |> range(start: -1h)
#         |> filter(fn: (r) => r["_measurement"] == "test_measurement")
#     '''

#     query_api = client.query_api()
#     result = query_api.query(query=query)

#     print("\nПрочитанные данные:")
#     for table in result:
#         for record in table.records:
#             print(f"Значение: {record.get_value()}, Время: {record.get_time()}")

# except Exception as e:
#     print(f"Ошибка: {str(e)}")

# finally:
#     client.close()