from src.services import learning_service


next_review, new_strength = learning_service.calculate_next_review(0,True)
print(f"New word correct {new_strength}, review in {next_review}")

nextr, news = learning_service.calculate_next_review(4, False)
print(f"strong word: {news} review in {nextr}") 
