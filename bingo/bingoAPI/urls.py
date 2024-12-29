from django.urls import path
from . import views

urlpatterns = [
    path('register-to-game', views.RegisterToGameView.as_view(), name='register_to_game'),
    path('claim-win', views.ClaimWinView.as_view(), name='claim_win'),
    path('bingo-card', views.GetBingoCardView.as_view(), name='get_bingo_card'),
]
