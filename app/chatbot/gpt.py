"""
ChatGPT 를 쉽게 사용하기 위한 OpenAPI 의 추상화 클래스입니다.
"""
import openai

class ChatGPT:
    """
    ChatGPT 를 쉽게 사용하기 위한 OpenAPI 의 추상화 클래스입니다.
    """

    def __init__(
        self,
        key: str,
        default_model: str,
        instructions: str,
    ):
        self.key = key
        self.default_model = default_model
        self.client = openai.OpenAI(api_key=key)
        self.instructions = instructions
        self.clear()

    def chat(
        self,
        query: str,
    ):
        """
        ChatGPT 로 대화 내용을 전송합니다.

        Args:
            model (_type_): _description_
            query (_type_): _description_

        Returns:
            _type_: _description_
        """
        user_query: list[dict[str, str]] = [
            {"role": "user", "content": query},
        ]
        send_query = self.chat_log + user_query
        response = self.client.chat.completions.create(
            model = self.default_model,
            messages = send_query
        )
        answer = response.choices[0].message.content

        self.chat_log.append({"role": "assistant", "content": answer})
        return answer

    def clear(self):
        """_summary_
            ChatGPT 의 대화 내용을 초기화합니다.
        """
        self.chat_log = [
            {
                "role": 
                    "system", 
                    "content": self.instructions
            }
        ]

    def create_image(
        self,
        prompt: list,
        part: int,
    ):
        """
        ChatGPT 로 이미지를 생성합니다.

        Args:
            prompt (_type_): _description_

        Returns:
            _type_: _description_
        """
        style = "anime style"
        # style = "oil painting style"
        # style = "watercolor painting style"
        # style = "impressionist painting style"
        # style = "pointillism painting style"
        # style = "abstract painting style"
        # style = "cubism painting style"
        # style = "expressionism painting style"
        # style = "fauvism painting style"
        # style = "pop art painting style"
        # style = "surrealism painting style"
        # style = "pencil sketch style"
        #style = "수채화 스타일"

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=str(prompt)+'\n\n앞의 내용을 포괄하는 ' + style + '의 일러스트 생성. 배경은 1970년대 한국.' + 'part ' + str(part) + '에 해당하는 일러스트.',
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        return image_url
