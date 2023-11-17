from openai import OpenAI

def get_open_ai_api_chat_response(prompt):
    print(prompt)
    api_key = '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'
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "我會列出幾種食材請跟我說我可以做出什麼料理並列出料理的步驟並列出需要的調味料以下是輸出的順序你可以做「」，以下是需要的食材&調味料料理的步驟如下:"},
             #{"role": "system", "content": "翻譯成英文用列表輸出"},
            {"role": "user", "content": prompt}
        ]
    )

    ai_answer2 = completion.choices[0].message.content
    ai_answer = ai_answer2.replace('\n', '<br>')


    print(ai_answer)
    return ai_answer
