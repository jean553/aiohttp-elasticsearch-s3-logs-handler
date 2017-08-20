---
actions:
  1:
    action: snapshot
    description: >
      Attempt to create AWS S3 snapshot
    options:
      repository: "backups"
      name: "backups_%Y_%m_%d"
    filters:
      - filtertype: pattern
        kind: prefix
        value: data-
