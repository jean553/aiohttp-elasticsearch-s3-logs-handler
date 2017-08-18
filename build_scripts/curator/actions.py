---
actions:
  1:
    action: snapshot
    description: >
      Attempt to create AWS S3 snapshot
    options:
      repository: "s3-backup"
      name: "s3_backup_%Y_%m_%d"
    filters:
      - filtertype: pattern
        kind: prefix
        value: data-
