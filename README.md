# Monitor da Caixa Misteriosa (WebContinental)

A cada 10 minutos, o GitHub Actions abre a página da Caixa Misteriosa e lê os contadores
"Caixas já foram liberadas" e "Caixas ainda disponíveis". Quando o número de liberadas muda,
manda um alerta no Telegram.

## 1. Criar o bot no Telegram
1. No Telegram, abra o **@BotFather** e envie `/newbot`. Escolha um nome e um usuário (precisa terminar em `bot`).
2. Ele responde com um **token** (algo como `123456:ABC-xyz...`). Guarde.
3. Abra o seu bot e mande qualquer mensagem (ex.: `oi`).
4. No navegador, acesse `https://api.telegram.org/botSEU_TOKEN/getUpdates` (troque `SEU_TOKEN`).
   Procure `"chat":{"id":123456789` — esse número é o seu **chat id**.

## 2. Criar o repositório no GitHub
1. Crie um repositório novo, **público** (aí os minutos do Actions são grátis e ilimitados).
   O token fica guardado nos Secrets, então ele não aparece pra ninguém.
2. Suba os arquivos mantendo a estrutura:
   ```
   verificar.py
   README.md
   .github/workflows/caixa.yml
   ```
   Pelo site: **Add file → Upload files** e arraste a pasta inteira. Ou, em **Create new file**,
   digite `.github/workflows/caixa.yml` como nome. As barras criam as pastas.

## 3. Cadastrar os segredos
Em **Settings → Secrets and variables → Actions → New repository secret**, crie:
- `TELEGRAM_TOKEN`: o token do BotFather
- `TELEGRAM_CHAT_ID`: o seu chat id

## 4. Testar
Vá em **Actions → Monitor Caixa Misteriosa → Run workflow**. Em menos de 1 minuto você deve
receber: "✅ Monitor da Caixa Misteriosa ativado!" com os números atuais.
Depois disso ele roda sozinho a cada ~10 minutos.

## Observações
- O agendamento do GitHub pode atrasar alguns minutos nos horários de pico.
- Se o site mudar o layout ou bloquear o acesso, você recebe um aviso ⚠️ uma única vez.
- Quando a promoção acabar (30/11), desative em **Actions → Monitor Caixa Misteriosa → ⋯ → Disable workflow**.
