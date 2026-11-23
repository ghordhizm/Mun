for i in $(seq 1 30); do
  node /tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad/bin/sendgb.js "https://www.sendgb.com/en/download/AurrM47ezBC" /tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad/mixlab > /tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad/mixlab/sgb_try.txt 2>&1
  if ! grep -q "Temporarily Unavailable" /tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad/mixlab/sgb_try.txt; then echo "AVAILABLE after try $i"; exit 0; fi
  sleep 120
done
echo "STILL DOWN after 60 min"
