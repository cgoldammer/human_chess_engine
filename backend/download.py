import boto3
import chess

s3 = boto3.client('s3')
print('start')
s3.download_file('humanchess', 'moves.h5', 'moves.h5')
print('end')

