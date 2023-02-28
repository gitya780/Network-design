set /p SenderCorruptPercent= "input SenderCorruptPercent: "
set /p SenderPacketDropPercent= "input SenderPacketDropPercent: "
set /p window= "input window: "

set /p ReceiverCorruptPercent= "input ReceiverCorruptPercent: "
set /p ReceiverDropPercent= "input ReceiverDropPercent: "

start /B python3 UDPServer_ImageReceive.py %ReceiverCorruptPercent% %ReceiverDropPercent%
timeout 1
start /B python3 UDPServer_ImageSend.py %SenderCorruptPercent% %SenderPacketDropPercent% %window%