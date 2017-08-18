---
actions:
  1:
    action: snapshot
    repository: "my_repository"
    description: >
      Attempt to create AWS S3 snapshot
    options:
      name: 'curator-%Y-%m-%d'
