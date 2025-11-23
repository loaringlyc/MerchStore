from kafka import KafkaConsumer

def monitor_logs():
    # 创建 Kafka 消费者
    consumer = KafkaConsumer(
        'log-channel',  # 替换为你的 topic 名称
        bootstrap_servers=['localhost:9093'],  # 替换为你的 Kafka broker 地址
        auto_offset_reset='earliest',  # 从最早的消息开始消费
        enable_auto_commit=True,  # 自动提交偏移量
        group_id='log-monitor-group'  # 消费者组 ID
    )

    print("Monitoring logs from Kafka topic 'logs'...")
    try:
        for message in consumer:
            print(f"Received log: {message.value.decode('utf-8')}")
    except KeyboardInterrupt:
        print("Stopped monitoring logs.")
    finally:
        consumer.close()

if __name__ == "__main__":
    monitor_logs()