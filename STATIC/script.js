const API_URL = "";
let movieFetchController = null;
let activeGenreId = null;
let actionCooldown = false;

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
let isLoggedIn = true;  // För att tvinga testläge

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


let genres = [];

async function fetchGenres() {
  displayGenres(true);

  try {
    const res = await fetch("/api/genres");
    const data = await res.json();
    genres = data.genres || [];

    displayGenres();

    //fetchAdditionalGenres();
  } catch (err) {
    console.error("Error fetching genres:", err);
  }
}

function displayGenres(initial = false) {
  genrePanel.innerHTML = '';

  if (genres.length === 0 && initial) {
    genrePanel.innerHTML = '<div>Laddar genrer...</div>';
    return;
  }

  genres.forEach((genre) => {
    const genreItem = document.createElement('div');
    genreItem.textContent = genre.name;
    genreItem.classList.add('genre-item');
    genreItem.addEventListener('click', () => {
      currentIndex = 0;
      fetchMovies(genre.id);
    });
    genrePanel.appendChild(genreItem);
  });
}
async function fetchAdditionalGenres() {
  try {
    const res = await fetch(`${API_URL}/api/genres/full`);
    const data = await res.json();
    if (data.genres) {
      genres = data.genres;
      displayGenres();
    }
  } catch (err) {
    console.error("Error fetching full genre list:", err);
  }
}
async function fetchMovies(genreId = null) {
  if (movieFetchController) {
    movieFetchController.abort();
  }

  movieFetchController = new AbortController();
  const signal = movieFetchController.signal;

  activeGenreId = genreId;

  try {
    let url = `${API_URL}/api/movies?page=1`;
    if (genreId) url += `&genre_id=${genreId}`;

    const res = await fetch(url, { signal });
    const data = await res.json();
    if (activeGenreId !== genreId) return;

    movies = shuffle(data.results || []);
    currentIndex = 0;
    showNextMovie();

    loadAdditionalMovies(genreId, signal);
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log("Första sida avbröts.");
    } else {
      console.error("Fel vid hämtning av filmer:", err);
    }
  }
}
async function loadAdditionalMovies(genreId = null, signal) {
  const additionalMovies = [];

  for (let i = 2; i <= 40; i++) {
    if (activeGenreId !== genreId) return;

    let url = `${API_URL}/api/movies?page=${i}`;
    if (genreId) url += `&genre_id=${genreId}`;

    try {
      const res = await fetch(url, { signal });
      const data = await res.json();

      if (activeGenreId !== genreId) return;

      additionalMovies.push(...(data.results || []));
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log(`Bakgrundsladdning av sida ${i} avbröts.`);
        return;
      } else {
        console.error(`Fel vid hämtning av sida ${i}:`, err);
      }
    }
  }

  if (activeGenreId !== genreId) return;

  movies.push(...shuffle(additionalMovies));
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
  let startX = 0;
  let diffX  = 0;
  let dragging = false;

  const getClientX = (e) =>
    e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;

  const start = (e) => {
    dragging = true;
    startX = getClientX(e);
    diffX  = 0;

    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup',   end);
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend',  end);
    window.addEventListener('touchcancel', end);
  };

  const move = (e) => {
    if (!dragging) return;
    diffX = getClientX(e) - startX;
    card.style.transform = `translateX(${diffX}px) rotate(${diffX / 20}deg)`;
    if (e.cancelable) e.preventDefault();
  };

  const end = () => {
    if (!dragging) return;
    dragging = false;
    if (actionCooldown) return;
    
    if (diffX > 50) {
      likeMovie(movie);
      animateSwipe(card, 'right');
      setCooldown();
    } else if (diffX < -50) {
      discardMovie(movie);
      animateSwipe(card, 'left');
      setCooldown();
    }
    
    window.removeEventListener('mousemove', move);
    window.removeEventListener('mouseup',   end);
    window.removeEventListener('touchmove', move);
    window.removeEventListener('touchend',  end);
    window.removeEventListener('touchcancel', end);

    if (diffX > 50) {
      likeMovie(movie);
      animateSwipe(card, 'right');
    } else if (diffX < -50) {
      discardMovie(movie);
      animateSwipe(card, 'left');
    } else {
      card.style.transition = 'transform 0.25s ease';
      card.style.transform  = 'translateX(0) rotate(0)';
      setTimeout(() => (card.style.transition = ''), 250);
    }
  };

  card.addEventListener('mousedown', start);
  card.addEventListener('touchstart', start, { passive: true });
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
  if (!isLoggedIn) return;
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
  if (!currentCard || actionCooldown) return;
  likeMovie(movies[currentIndex]);
  animateSwipe(currentCard, "right");
  setCooldown();
});

dislikeBtn.addEventListener("click", () => {
  if (!currentCard || actionCooldown) return;
  discardMovie(movies[currentIndex]);
  animateSwipe(currentCard, "left");
  setCooldown();
});

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
document.addEventListener("keydown", (event) => {
  if (!currentCard || actionCooldown) return;

  switch (event.key) {
    case "ArrowRight":
      likeMovie(movies[currentIndex]);
      animateSwipe(currentCard, "right");
      setCooldown();
      break;
    case "ArrowLeft":
      discardMovie(movies[currentIndex]);
      animateSwipe(currentCard, "left");
      setCooldown();
      break;
  }
});

function setCooldown() {
  actionCooldown = true;
  setTimeout(() => {
    actionCooldown = false;
  }, 500);
}

fetchGenres();
fetchMovies();

document.getElementById("show-liked-btn").addEventListener("click", async () => {
  const section = document.getElementById("liked-movies-section");
  const list = document.getElementById("liked-movies-list");
  section.style.display = "block"; // Visa sektionen
  list.innerHTML = "<p>Laddar gillade filmer...</p>";
  console.log("Knappen klickades!");


  try {
    const res = await fetch("/api/liked", { credentials: "include" });
    const data = await res.json();
    if (data && data.movies && data.movies.length > 0) {
      list.innerHTML = "";
      data.movies.forEach((movie) => {
        const card = document.createElement("div");
        card.classList.add("movie-tile");
        card.innerHTML = `
          <img src="https://image.tmdb.org/t/p/w200${movie.poster_path || ''}" alt="Poster">
          <p>${movie.title}</p>
        `;
        list.appendChild(card);
      });
    } else {
      list.innerHTML = "<p>Inga gillade filmer än.</p>";
    }
  } catch (err) {
    console.error("Fel vid hämtning av gillade filmer:", err);
    list.innerHTML = "<p>Kunde inte hämta filmer.</p>";
  }
});
