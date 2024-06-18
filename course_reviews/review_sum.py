import boto3
import pandas as pd
from io import StringIO, BytesIO
import json


def summ(row):
    try:
        review = row['review']
        review = str(review)
    
        if len(review) < 150:
            # print('e')
            return review
        
        bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    
        prompt = review + "\n위 강의평들을 75글자 정도로 요약해줘. 다른 말은 할 필요없고, 요약된 정보만 출력해줘."
    
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.5,
            "messages": [
                {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
                }
            ],
        }
    
        request=json.dumps(native_request)
    
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
        response = bedrock_runtime.invoke_model(modelId=model_id, body=request)
        model_response = json.loads(response["body"].read())
        response_text = model_response["content"][0]["text"]
        
        # print('d')
        return response_text
        
    except Exception as e:
        print(e)
        return review


s3_client = boto3.client('s3')

bucket_name = 'int-s3-bedrock-data-source-us'
file_key = 'test/review.csv'

csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
body = csv_obj['Body']
csv_string = body.read().decode('utf-8')


df = pd.read_csv(StringIO(csv_string))

print(df.info())



total = len(df)
done = 0


for index, row in df.iterrows():
    done += 1
    df.loc[index, 'review'] = summ(row)
    print(str(done) + "/" + str(total))

csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)
s3_client.put_object(Bucket=bucket_name, Key='reviews/review_sum.csv', Body=csv_buffer.getvalue())
print("s3에 저장 완료")

bucket_name = 'int-s3-bedrock-data-source-us'
file_key = "/reviews/review_sum.csv"

csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
body = csv_obj['Body']
csv_string = body.read().decode('utf-8')

df = pd.read_csv(StringIO(csv_string))

for index, row in df.iterrows():
    text = str(row['course_name']) + '\n' + str(row['professor']) + "\n" + str(row['review']) + "\n" + str(row['rating'])
    filename = f"/reviews/split/{index}.txt"

    text_buffer = StringIO()
    text_buffer.write(text)
    s3_client.put_object(Bucket=bucket_name, Key=filename, Body=text_buffer.getvalue())
    print(f"{index}.txt 저장 완료료")