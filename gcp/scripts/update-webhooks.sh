#!/bin/sh
# Re-point Razorpay webhook to current public URL after VM restart (ephemeral IP).
PUBLIC_IP=$(curl -s --max-time 15 https://ifconfig.me 2>/dev/null || true)
if [ -z "$PUBLIC_IP" ]; then echo "[webhooks] public IP not available yet"; exit 0; fi
NEW_URL="http://$PUBLIC_IP/webhook/fk-razorpay-pay"
if [ -n "${RAZORPAY_KEY_ID:-}" ] && [ -n "${RAZORPAY_KEY_SECRET:-}" ] && [ -n "${RAZORPAY_WEBHOOK_ID:-}" ]; then
  B64=$(printf '%s:%s' "$RAZORPAY_KEY_ID" "$RAZORPAY_KEY_SECRET" | base64 | tr -d '\n')
  WHSEC=$(cat /opt/secrets/razorpay_webhook_secret 2>/dev/null || true)
  CUR=$(curl -s -H "Authorization: ***$B64" -H "Accept: application/json" "https://api.razorpay.com/v1/webhooks" --max-time 25 \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(next((w['url'] for w in d.get('items',[]) if w['id']=='$RAZORPAY_WEBHOOK_ID'),''))" 2>/dev/null || echo "")
  if [ "$CUR" != "$NEW_URL" ]; then
    curl -s -X PUT -H "Authorization: ***$B64" -H "Content-Type: application/json" -H "Accept: application/json" \
      -d "{\"url\":\"$NEW_URL\",\"events\":{\"payment.captured\":true,\"payment.authorized\":true,\"payment.failed\":true,\"payment_link.paid\":true},\"secret\":\"$WHSEC\"}" \
      "https://api.razorpay.com/v1/webhooks/$RAZORPAY_WEBHOOK_ID" --max-time 30 >/dev/null 2>&1 \
      && echo "[webhooks] razorpay re-pointed -> $NEW_URL" || echo "[webhooks] WARN re-point failed"
  else
    echo "[webhooks] razorpay url ok"
  fi
fi
exit 0
