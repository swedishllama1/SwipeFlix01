const API_KEY = '72dd7b5804849fa9be8b72edfe8abdc1';
const BASE_URL = 'https://api.themoviedb.org/3';
const container = document.getElementById('movie-container');
const likeBtn = document.getElementById('like-btn');
const dislikeBtn = document.getElementById('dislike-btn');
let movies = [];
let currentIndex = 0;
let likedMovies = [];
let currentCard = null;

async function fetchMovies() {
  const res = await fetch(`${BASE_URL}/movie/popular?api_key=${API_KEY}&language=en-US&page=1`);
  const data = await res.json();
  movies = data.results;
  showNextMovie();
}

function showNextMovie() {
  if (currentIndex >= movies.length) {
    alert("No more movies!");
    return;
  }

  const movie = movies[currentIndex];
  const card = document.createElement('div');
  card.className = 'movie-card';
  card.style.backgroundImage = `url(https://image.tmdb.org/t/p/w500${movie.poster_path})`;
  card.innerHTML = `<h2>${movie.title}</h2>`;
  container.innerHTML = '';
  container.appendChild(card);
  currentCard = card;

  addSwipeHandlers(card, movie);
}

function addSwipeHandlers(card, movie) {
  let offsetX = 0;
  let isDragging = false;

  const onDragStart = (e) => {
    isDragging = true;
    offsetX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
  };

  const onDragMove = (e) => {
    if (!isDragging) return;
    const currentX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
    const diffX = currentX - offsetX;
    card.style.transform = `translateX(${diffX}px) rotate(${diffX / 20}deg)`;
  };

  const onDragEnd = (e) => {
    if (!isDragging) return;
    isDragging = false;
    const endX = e.type.includes('touch') ? e.changedTouches[0].clientX : e.clientX;
    const diffX = endX - offsetX;

    if (diffX > 100) {
      likeMovie(movie);
      animateSwipe(card, 'right');
    } else if (diffX < -100) {
      discardMovie(movie);
      animateSwipe(card, 'left');
    } else {
      card.style.transform = 'translateX(0px) rotate(0deg)';
    }
  };

  card.addEventListener('mousedown', onDragStart);
  card.addEventListener('mousemove', onDragMove);
  card.addEventListener('mouseup', onDragEnd);
  card.addEventListener('touchstart', onDragStart);
  card.addEventListener('touchmove', onDragMove);
  card.addEventListener('touchend', onDragEnd);
}

function animateSwipe(card, direction) {
  card.classList.add(direction === 'right' ? 'liked' : 'disliked');
  card.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
  card.style.transform = `translateX(${direction === 'right' ? '500px' : '-500px'}) rotate(${direction === 'right' ? '45deg' : '-45deg'})`;
  card.style.opacity = '0';

  setTimeout(() => {
    currentIndex++;
    showNextMovie();
  }, 400);
}

function likeMovie(movie) {
  likedMovies.push(movie);
  console.log('Liked:', movie.title);
}

function discardMovie(movie) {
  console.log('Discarded:', movie.title);
}

// Handle button clicks
likeBtn.addEventListener('click', () => {
  if (!currentCard) return;
  likeMovie(movies[currentIndex]);
  animateSwipe(currentCard, 'right');
});

dislikeBtn.addEventListener('click', () => {
  if (!currentCard) return;
  discardMovie(movies[currentIndex]);
  animateSwipe(currentCard, 'left');
});

fetchMovies();
