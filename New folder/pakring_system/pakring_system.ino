#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32_Servo.h>
#include <Firebase_ESP_Client.h>
#define SS_PIN 5
#define RST_PIN 27
int lcdColumns = 16;
int lcdRows = 2;
int sen1 =26;
int sen2 =25;
byte led1 = 0;
byte led2 = 0;
Servo myservo;
MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows); 
const char * ssid ="Redmi 9T";
const char * psw ="rameez123";
void Network_Connection(void);

unsigned long startTime = 0;
byte flag =0;
/////////////////////////firbase////////////////////////////////////////
#define DATABASE_URL "https://smart-parking-system-edcde-default-rtdb.firebaseio.com/" 
#define DATABASE_SECRET "eculZMkWFUUkjZEmIWAFwy29msY2"
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
unsigned long dataMillis = 0;
unsigned long dataMillis_2 = 0;
int count =0;
void firbase_fun_send_s_1( int data_sand)
{ 
    if (millis() - dataMillis > 5000)
    {
        dataMillis = millis();
        Serial.printf("Set int... %s, slot_1  ,%d\n", Firebase.RTDB.setInt(&fbdo,"/slot_1",data_sand) ? "ok" : fbdo.errorReason().c_str(),data_sand);
    }
}
void firbase_fun_send_s_2( int data_sand)
{ 
    if (millis() - dataMillis_2 > 5000)
    {
        dataMillis_2 = millis();
        Serial.printf("Set int... %s, slot_2  ,%d\n", Firebase.RTDB.setInt(&fbdo,"/slot_2",data_sand) ? "ok" : fbdo.errorReason().c_str(),data_sand);
    }
}
void firbase_fun_init()
{ 
  Serial.printf("Firebase Client v%s\n\n", FIREBASE_CLIENT_VERSION);
  config.database_url = DATABASE_URL;
  config.signer.tokens.legacy_token = DATABASE_SECRET;
  Firebase.begin(&config, &auth);
}
//////////////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(9600);
  lcd.init();
  // turn on LCD backlight                      
  lcd.backlight();
  SPI.begin();
  Network_Connection();
  Serial.println("Please put your card..");
  rfid.PCD_Init();
  myservo.attach(13);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("   Please  ");
  lcd.setCursor(0,1);
  lcd.print(" Put Your Card ");
  pinMode(sen1,INPUT);
  pinMode(sen2,INPUT);
  firbase_fun_init();
}

void loop() 
{
 if (millis()-startTime >= 6000 && flag)
 {
    flag =0;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("   Please  ");
    lcd.setCursor(0,1);
    lcd.print(" Put Your Card ");
 }
  if (  rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial())
  {
    Serial.print("NUID tag is :");
    delay(2);
    String ID = "";
    for (byte i = 0; i < rfid.uid.size; i++) 
    {
      Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
      Serial.print(rfid.uid.uidByte[i], HEX);
      ID.concat(String(rfid.uid.uidByte[i] < 0x10 ? " 0" : " "));
      ID.concat(String(rfid.uid.uidByte[i], HEX));
      delay(30);
     }
     Serial.println();
     ID.toUpperCase();
     if (ID.substring(1) == "43 B6 8E A9" && led1 == 0 ) 
     {
        Serial.println("LED1 is ON..");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("   WELCOME  ");
        lcd.setCursor(0,1);
        lcd.print(" Your Solt Is 1 ");
        startTime = millis();
        myservo.write(180);
        delay(5000);
         myservo.write(0);
        led1 = 1;
        flag =1;
     } 
     else if (ID.substring(1) == "43 B6 8E A9" && led1 == 1 ) 
     {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("   GOOD BYE  ");
        lcd.setCursor(0,1);
        lcd.print("Have a Nice Day");
        Serial.println("LED1 is OFF..");
        startTime = millis();
        myservo.write(180);
        delay(5000);
         myservo.write(0);
        led1 = 0;
        flag =1;
     }
     else if (ID.substring(1) == "90 91 42 20" && led2 == 0 ) 
     {
        Serial.println("led2 is ON..");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("   WELCOME  ");
        lcd.setCursor(0,1);
        lcd.print(" Your Solt Is 2 ");
        startTime = millis();
        myservo.write(180);
        delay(5000);
         myservo.write(0);
        led2 = 1;
        flag =1;
     } 
     else if (ID.substring(1) == "90 91 42 20" && led2 == 1 ) 
     {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("   GOOD BYE  ");
        lcd.setCursor(0,1);
        lcd.print("Have a Nice Day");
        Serial.println("led2 is OFF..");
        startTime = millis();
        myservo.write(180);
        delay(5000);
         myservo.write(0);
        led2 = 0;
        flag =1;
     }
     else
     {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print(" Please Check ");
        lcd.setCursor(0,1);
        lcd.print(" Your Booking ");
        startTime = millis();
        flag =1;
     }
  }
 if(led1 && !digitalRead(sen1))
 {
    firbase_fun_send_s_1(1);
 }
 else
 {
    firbase_fun_send_s_1(0);
 }
 if(led2 && !digitalRead(sen2))
 {
    firbase_fun_send_s_2(1);
 }
 else
 {
   firbase_fun_send_s_2(0);
 }
delay(200);
}

void Network_Connection(void)
{
  WiFi.begin(ssid, psw);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("   Connecting  ");
  lcd.setCursor(0,1);
  lcd.print("To Your Network ");
  Serial.println("LED1 is OFF..");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}
