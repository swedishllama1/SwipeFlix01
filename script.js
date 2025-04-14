const API_KEY = '72dd7b5804849fa9be8b72edfe8abdc1';
const BASE_URL = 'https://api.themoviedb.org/3';
const API_URL = "http://localhost:5000"; // Adjust if needed

const container = document.getElementById('movie-container');
const likeBtn = document.getElementById('like-btn');
const dislikeBtn = document.getElementById('dislike-btn');
const userIcon = document.getElementById("user-icon");
const authPanel = document.getElementById("auth-panel");
const userMenu = document.getElementById("user-menu");


const genreMenu = document.getElementById("genre-menu");
const genreIcon = document.getElementById("genre-icon");
const genrePanel = document.getElementById("genre-panel");

let movies = [];
let currentIndex = 0;
let currentCard = null;
let isLoggedIn = false;

userIcon.addEventListener("click", (e) => {
  e.stopPropagation();
  userMenu.classList.toggle("locked");
});

document.addEventListener("click", (e) => {
  if (!userMenu.contains(e.target)) {
    userMenu.classList.remove("locked");
  }
});

genreIcon.addEventListener("click", (e) => {
  e.stopPropagation();
  genreMenu.classList.toggle("locked");
});

document.addEventListener("click", (e) => {
  if (!genreMenu.contains(e.target)) {
    genreMenu.classList.remove("locked");
  }
});

document.getElementById("login-btn").addEventListener("click", async () => {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (res.ok) {
    isLoggedIn = true;
    document.getElementById("auth-status").textContent = "Logged in!";
    document.getElementById("logout-btn").style.display = "inline";
  } else {
    document.getElementById("auth-status").textContent = data.error;
  }
});

document.getElementById("register-btn").addEventListener("click", async () => {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (res.ok) {
    document.getElementById("auth-status").textContent = "Registered! Now log in.";
  } else {
    document.getElementById("auth-status").textContent = data.error;
  }
});

document.getElementById("logout-btn").addEventListener("click", async () => {
  await fetch(`${API_URL}/logout`, {
    method: "POST",
    credentials: "include"
  });
  isLoggedIn = false;
  document.getElementById("auth-status").textContent = "Logged out";
  document.getElementById("logout-btn").style.display = "none";
});

let genres = [];

async function fetchGenres() {
  try {
    const res = await fetch(`${BASE_URL}/genre/movie/list?api_key=${API_KEY}&language=en-US`);
    const data = await res.json();
    genres = data.genres || [];
    displayGenres();
  } catch (err) {
    console.error("Error fetching genres:", err);
  }
}

function displayGenres() {
  genrePanel.innerHTML = '';

  genres.forEach((genre) => {
    const genreItem = document.createElement('div');
    genreItem.textContent = genre.name;
    genreItem.classList.add('genre-item');
    genreItem.addEventListener('click', () => {
      currentIndex = 0; 
      fetchMovies(40, genre.id);
    });
    genrePanel.appendChild(genreItem);
  });
}

async function fetchMovies(pages = 40, genreId = null) {
  const allMovies = [];
  for (let i = 1; i <= pages; i++) {
    let url = `${BASE_URL}/movie/popular?api_key=${API_KEY}&language=en-US&page=${i}`;
    if (genreId) {
      url = `${BASE_URL}/discover/movie?api_key=${API_KEY}&language=en-US&page=${i}&with_genres=${genreId}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    allMovies.push(...(data.results || []));
  }

  movies = shuffle(allMovies);
  showNextMovie();
}

function showNextMovie() {
  if (currentIndex >= movies.length) {
    document.getElementById('movie-info').innerHTML = "<p>No more movies!</p>";
    container.innerHTML = '';
    return;
  }

  const movie = movies[currentIndex];
  const card = document.createElement('div');
  card.className = 'movie-card';

  const posterPath = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : 'https://via.placeholder.com/300x450?text=No+Image';

  const rating = movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A';
  const releaseDate = movie.release_date || 'Unknown';
  const fullDescription = movie.overview || 'No description available.';

  card.style.backgroundImage = `url(${posterPath})`;
  container.innerHTML = '';
  container.appendChild(card);
  currentCard = card;

  document.getElementById('movie-info').innerHTML = `
    <h2>${movie.title}</h2>
    <p class="meta">⭐ ${rating} | 📅 ${releaseDate}</p>
    <div class="description">${fullDescription}</div>
  `;

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
    const endX = e.type.includes('touch')
      ? e.changedTouches[0].clientX
      : e.clientX;
    const diffX = endX - offsetX;

    if (diffX > 50) {
      likeMovie(movie);
      animateSwipe(card, 'right');
    } else if (diffX < -50) {
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
  card.style.transform = `translateX(${
    direction === 'right' ? '500px' : '-500px'
  }) rotate(${direction === 'right' ? '45deg' : '-45deg'})`;
  card.style.opacity = '0';

  setTimeout(() => {
    currentIndex++;
    showNextMovie();
  }, 400);
}

function likeMovie(movie) {
  if (!isLoggedIn) {
    return;
  }
  fetch(`${API_URL}/like`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(movie)
  })
    .then((res) => res.json())
    .then((data) => console.log("Liked:", data))
    .catch((err) => console.error("Error liking movie:", err));
}

function discardMovie(movie) {
  console.log("Discarded:", movie.title);
}

likeBtn.addEventListener("click", () => {
  if (!currentCard) return;
  likeMovie(movies[currentIndex]);
  animateSwipe(currentCard, "right");
});

dislikeBtn.addEventListener("click", () => {
  if (!currentCard) return;
  discardMovie(movies[currentIndex]);
  animateSwipe(currentCard, "left");
});

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

fetchGenres();

fetchMovies();