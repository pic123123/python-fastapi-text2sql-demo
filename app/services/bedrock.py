import boto3
from langchain_aws import ChatBedrock


def get_bedrock_llm():
    client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")

    llm = ChatBedrock(
        client=client,
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs={"temperature": 0},
    )
    return llm
