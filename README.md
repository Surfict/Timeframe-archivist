# Object
This project is designed to allow automatic videos upload to different services (S3, Nextcloud) from a phone, connected to a computer. 
It is designed for someone who is creating videos at regular and recurring events, and want to have an automatic way to upload and archive the created content by simply plugging their phone and executing a script.

Some features : 

- Upload to S3 (optional)
- Upload to nextcloud (optional)
- Automatic naming - with some options like including the date (optional)
- Alert on Telegram to be alerted when the archiving is done, or to have a link to share the uploaded video from nextcloud (optional)
- Automatic deletion on the phone afer upload (optional)
- S3 Storage type selection (if using S3 upload)

It is designed to work with the following stack : 

- Phones : Android, Iphone
- Computer : windows


# Run

1) Fill the file events.yml to your liking

2) Copy past the env-example to .env, and fill it (WIP)

3) Run
```
docker compose run timeframe_archivist
```

