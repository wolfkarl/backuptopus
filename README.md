# Backuptopus 🦑

A dockerized Python script that backs up folders and PG into a single tar.gz file, including mattermost notifications and backup rotation.

Example Docker Compose Config:
```yml
backup:
    build: ../backuptopus
    volumes:
      - ./mattermost:/mnt/mattermost
      - ./backups:/mnt/backups
    environment:
      MMS_WEBHOOK: "http://..."
      BACKUP_DIR: "/mnt/backups"
      FILE_TARGETS: "/mnt/mattermost"
      PG_TARGETS: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/${POSTGRES_DB}"
```