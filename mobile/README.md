# FinanSys Mobile

Aplicativo Expo que consome a API REST do FinanSys.

1. Defina `EXPO_PUBLIC_API_URL` com o endereço do computador na rede, por exemplo `http://192.168.1.20:8000`.
2. Se o backend usar `FINANSYS_API_TOKEN`, defina o mesmo valor em `EXPO_PUBLIC_API_TOKEN`.
3. No backend, use `FINANSYS_HOST=0.0.0.0` somente em uma rede confiável e configure um token antes de expor a API.
4. Execute `npm install` e `npm start` nesta pasta.

O aplicativo não deve ser apontado para uma instalação pública sem autenticação, HTTPS e banco de dados apropriado.
