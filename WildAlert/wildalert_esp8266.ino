#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,16,2);

#define LED_PIN D6
#define BUZZER_PIN D5

const char* ssid = "GNXS-48a548";
const char* password = "200C8648A548";

const char* mqtt_server = "broker.hivemq.com";
const char* mqtt_topic  = "wildalert/test";

WiFiClient espClient;
PubSubClient client(espClient);

bool alertActive=false;
bool alertLocked=false;

/* timers */
unsigned long lastAlertTime=0;
unsigned long lastBlink=0;
unsigned long lastScroll=0;

const int alertTimeout=3000;
const int blinkInterval=500;
const int scrollInterval=350;

/* text */
String goSlowText="   Go Slow   ";
String stopText="   STOP! STOP! STOP!   ";

int scrollIndex=0;


/* NORMAL MODE */

void showNormal()
{
alertActive=false;
alertLocked=false;
scrollIndex=0;

digitalWrite(LED_PIN,LOW);
digitalWrite(BUZZER_PIN,HIGH);
}


/* ALERT MODE */

void showAlert()
{
alertActive=true;
alertLocked=false;
lastAlertTime=millis();
}


/* LOCKED ALERT (image upload) */

void showLockedAlert()
{
alertActive=true;
alertLocked=true;
}


/* MQTT */

void callback(char* topic, byte* payload, unsigned int length)
{

String message="";

for(int i=0;i<length;i++)
message+=(char)payload[i];

message.trim();

if(message=="ALERT")
showAlert();

else if(message=="ALERT_LOCK")
showLockedAlert();

else if(message=="CLEAR")
showNormal();

}


/* MQTT reconnect */

void reconnect()
{
while(!client.connected())
{
if(client.connect("WildAlertESP"))
{
client.subscribe(mqtt_topic);
showNormal();
}
else
delay(2000);
}
}


void setup()
{

pinMode(LED_PIN,OUTPUT);
pinMode(BUZZER_PIN,OUTPUT);

digitalWrite(BUZZER_PIN,HIGH);

lcd.init();
lcd.backlight();

/* startup */

lcd.setCursor(0,0);
lcd.print("WildAlert");

lcd.setCursor(0,1);
lcd.print("Starting...");
delay(2000);

/* wifi */

lcd.clear();
lcd.setCursor(0,0);
lcd.print("Connecting WiFi");

WiFi.mode(WIFI_STA);
WiFi.begin(ssid,password);

while(WiFi.status()!=WL_CONNECTED)
{
delay(500);
lcd.print(".");
}

lcd.clear();
lcd.setCursor(0,0);
lcd.print("WiFi Connected");
delay(1500);

/* mqtt */

client.setServer(mqtt_server,1883);
client.setCallback(callback);

showNormal();
}


void loop()
{

if(!client.connected())
reconnect();

client.loop();

unsigned long now=millis();

/* auto reset only if NOT locked */

if(alertActive && !alertLocked && (now-lastAlertTime>alertTimeout))
showNormal();


/* scroll text */

if(now-lastScroll>scrollInterval)
{

lastScroll=now;

String txt;

if(alertActive)
{
txt=stopText+stopText;

lcd.setCursor(0,0);
lcd.print(txt.substring(scrollIndex,scrollIndex+16));

lcd.setCursor(0,1);
lcd.print("Wildlife Crossing!");
}
else
{
txt=goSlowText+goSlowText;

lcd.setCursor(0,0);
lcd.print(txt.substring(scrollIndex,scrollIndex+16));

lcd.setCursor(0,1);
lcd.print("Speed Limit: 40 kmph");
}

scrollIndex++;

if(scrollIndex>=txt.length()-16)
scrollIndex=0;

}


/* LED + buzzer */

if(alertActive && (now-lastBlink>blinkInterval))
{

lastBlink=now;

static bool state=false;
state=!state;

digitalWrite(LED_PIN,state);
digitalWrite(BUZZER_PIN,state?LOW:HIGH);

}

}
