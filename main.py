import machine
import network
import ujson
import time-=
from umqtt.robust import MQTTClient

# ==========================================================
# 1. إعدادات الشبكة والـ MQTT
# ==========================================================
WIFI_SSID   = "Wokwi-GUEST"
WIFI_PASS   = ""

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID   = "esp32/teame47/h4"
TOPIC_SUB   = b"smarttraffic/intersection01/logic_decision"
TOPIC_PUB   = b"smarttraffic/intersection01/command"

# ==========================================================
# 2. إعداد الليدات (6 مجموعات / 12 ليد)
# ==========================================================
pin_ns_red = machine.Pin(23, machine.Pin.OUT)
pin_ns_yel = machine.Pin(22, machine.Pin.OUT)
pin_ns_grn = machine.Pin(21, machine.Pin.OUT)

pin_ew_red = machine.Pin(19, machine.Pin.OUT)
pin_ew_yel = machine.Pin(18, machine.Pin.OUT)
pin_ew_grn = machine.Pin(5, machine.Pin.OUT)

def set_leds(ns_r, ns_y, ns_g, ew_r, ew_y, ew_g):
    pin_ns_red.value(ns_r)
    pin_ns_yel.value(ns_y)
    pin_ns_grn.value(ns_g)
    pin_ew_red.value(ew_r)
    pin_ew_yel.value(ew_y)
    pin_ew_grn.value(ew_g)
    
    # طباعة الحالة في الـ console بعد كل تغيير
    print(f"NS: Red={ns_r}, Yellow={ns_y}, Green={ns_g} | EW: Red={ew_r}, Yellow={ew_y}, Green={ew_g}")

# ==========================================================
# 3. نشر الحالة الحالية
# ==========================================================
def publish_state(client):
    state = {
        "ns_red": pin_ns_red.value(),
        "ns_yel": pin_ns_yel.value(),
        "ns_grn": pin_ns_grn.value(),
        "ew_red": pin_ew_red.value(),
        "ew_yel": pin_ew_yel.value(),
        "ew_grn": pin_ew_grn.value()
    }
    msg = ujson.dumps(state)
    client.publish(TOPIC_PUB, msg)
    print("[Published]:", msg)

# ==========================================================
# 4. معالجة الداتا (المنطق)
# ==========================================================
def broker_data(topic, msg):
  try:
    payload = ujson.loads(msg.decode("utf-8"))
    print("\n[Received from Person 3]:", payload)

    # قراءة قرار Person 3 أو الأوامر المباشرة (Fallback)
    target_phase = payload.get("recommendedPhase") or payload.get("value")
    green_dur = payload.get("greenDuration", 10)
    yellow_dur = payload.get("yellow_duration", 3)

    if target_phase == "NS_GREEN":
      # 1. التبديل إلى الأصفر أولاً
      set_leds(0, 1, 0, 1, 0, 0)
      print(f"Yellow phase for {yellow_dur}s...")
      time.sleep(yellow_dur)

      # 2. التبديل إلى الأخضر للـ NS والأحمر للـ EW
      set_leds(0, 0, 1, 1, 0, 0)
      print(f"NS Green active for {green_dur}s...")

    elif target_phase == "EW_GREEN":
      # 1. التبديل إلى الأصفر أولاً
      set_leds(1, 0, 0, 0, 1, 0)
      print(f"Yellow phase for {yellow_dur}s...")
      time.sleep(yellow_dur)

      # 2. التبديل إلى الأخضر للـ EW والأحمر للـ NS
      set_leds(1, 0, 0, 0, 0, 1)
      print(f"EW Green active for {green_dur}s...")

    elif target_phase == "ALL_RED":
      set_leds(1, 0, 0, 1, 0, 0)

    # نشر الحالة الفعلية للعتاد إلى الـ Web
    publish_state(client)

  except Exception as e:
    print("Error in processing:", e)
# ==========================================================
# 5. الاتصال وإعادة الاتصال
# ==========================================================
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(broker_data)
    client.connect()
    client.subscribe(TOPIC_SUB)
    print("MQTT Connected Successfully! Waiting for commands...")
    return client

# اتصال الواي فاي
print("Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

while not wlan.isconnected():
    time.sleep(0.2)

print("WiFi Connected Successfully!")

# اتصال MQTT أول مرة
client = connect_mqtt()

# ==========================================================
# 6. التشغيل المستمر مع إعادة الاتصال + نشر دوري
# ==========================================================
while True:
    try:
        client.check_msg()
        client.ping()
        publish_state(client)   # نشر الحالة بشكل دوري
    except OSError as e:
        print("MQTT Error:", e)
        time.sleep(2)
        client = connect_mqtt()
    time.sleep(5)  # كل 5 ثواني ينشر الحالة
