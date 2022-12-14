import json
import gzip
import localstack_client.session as boto3
import rsa

QUEUE_URL = "http://localhost:4566/000000000001/login-queue"
QUEUE_NAME = "login-queue"

public_key, private_key = rsa.newkeys(512)
sqs = boto3.client("sqs")

# This follows a first in first out methodology and grabs the first message that is at the top of the queue.
# Returns a message body as a python dict and a receipt handle 
def get_message():
    res = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    for message in res.get("Messages", []):
        message_body = message["Body"]
        message_dict = json.loads(message_body)
        message_dict["receipt_handle"] = message["ReceiptHandle"]        
        return message_dict

# Masking the two confidential fields through public/private key encryption,
# this way duplicate values will be encoded in the same manner and will be able to 
# be spotted, as long as we keep track of the private keys. The rsa algorithm converts
# them to bytes but we will convert again to hex for slightly better readability.
# returns another dict, with the two values replaced with their masked counterparts.
def mask_fields(message_dict):
    masked_ip = rsa.encrypt(message_dict['ip'].encode(), public_key)
    masked_ip = masked_ip.hex()
    masked_device_id = rsa.encrypt(message_dict['device_id'].encode(), public_key)
    masked_device_id = masked_device_id.hex()
    message_dict['ip'] = masked_ip
    message_dict['device_id'] = masked_device_id
    return message_dict

# Combining the above two methods to form a read and tranform process
# also adding a catch if the data is faulty
def read_and_transform():
  while True:
    res = get_message()
    if res is None:
        print("Queue is depleted, stopping...")
        return
    if len(res) != 7:
        print("Wrong message type so cannot parse, moving to next one...")
        delete_from_top(res['receipt_handle'])
    else:
        break
  res = mask_fields(res)
  return res

# in FIFO fashion, once the message from the top is received, we will delete
# this message from the queue, continualy taking from the top until the whole
# queue is depleted

def delete_from_top(receipt_handle):
    sqs.delete_message(QueueUrl=QUEUE_URL,ReceiptHandle=receipt_handle)
    print("Message deleted with receipt handle" + receipt_handle)
