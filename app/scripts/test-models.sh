for m in gemini-3.8-flash gemini-3.5-flash-lite gemini-3.5-flash gemini-flash-latest gemini-flash-lite-latest gemini-2.5-flash gemini-3.1-flash-lite; do
  echo "== $m"
  curl -s -o /dev/null -w "%{http_code}\n" https://generativelanguage.googleapis.com/v1beta/openai/chat/completions \
    -H "Authorization: Bearer $LLM_API_KEY" -H "Content-Type: application/json" \
    -d "{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hi\"}]}"
done