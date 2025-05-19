from kog_ace_step.client_utils import generate_song

prompt = "caribean chill cuban dance music"

result = generate_song(prompt=prompt)

with open("output.wav", "wb") as f:
    f.write(result["audio_data"])
