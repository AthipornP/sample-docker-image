**Customer Portal** เป็นโปรเจคหลักเขียนด้วย Svelte ภายใน portal จะสามารถลิงก์ไปเปิดโปรเจคอื่นได้ โดยใช้ **SSO** ดังนี้
    - Django 
    - .NET
    - PHP

- ทุกโปรเจค implement OAuth มี Keycloak เป็น provider
- ทุกโปรเจครองรับการรันในรูปแบบของ container

## Development
- ทดสอบใน docker
- หลังแก้โค้ตเสร็จให้ build image ใหม่ทุกครั้ง