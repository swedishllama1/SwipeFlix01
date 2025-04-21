// ==============================
// API-konfiguration
// ==============================

// API-nyckel för att få tillgång till TMDb:s databas.
const API_KEY = '72dd7b5804849fa9be8b72edfe8abdc1';

// Grundadress för TMDb API-anrop.
const BASE_URL = 'https://api.themoviedb.org/3';

// Adress till lokal server för inloggning och gillade filmer.
const API_URL = "http://localhost:5000";

// ==============================
// DOM-element
// ==============================

// Hämtar elementet där filmer ska visas.
const container = document.getElementById('movie-container');

// Hämtar like-knappen från HTML.
const likeBtn = document.getElementById('like-btn');

// Hämtar dislike-knappen från HTML.
const dislikeBtn = document.getElementById('dislike-btn');

// Hämtar användarikonen från HTML.
const userIcon = document.getElementById("user-icon");

// Hämtar panelen för inloggning/registrering.
const authPanel = document.getElementById("auth-panel");

// Hämtar användarmenyn.
const userMenu = document.getElementById("user-menu");

// Hämtar genremenyn som öppnas.
const genreMenu = document.getElementById("genre-menu");

// Hämtar ikonen för att öppna genremenyn.
const genreIcon = document.getElementById("genre-icon");

// Hämtar panelen där genrerna listas.
const genrePanel = document.getElementById("genre-panel");

// ==============================
// Variabler
// ==============================

// Lista som lagrar filmer som hämtats.
let movies = [];

// Index för nuvarande film.
let currentIndex = 0;

// Referens till det nuvarande filmkortet.
let currentCard = null;

// Anger om användaren är inloggad.
let isLoggedIn = false;

// ==============================
// Användarmeny
// ==============================

// Öppnar/stänger användarmenyn när man klickar på ikonen.
userIcon.addEventListener("click", (e) => {
  e.stopPropagation(); // Stoppar klick från att bubbla upp.
  userMenu.classList.toggle("locked"); // Växlar synlighet.
});

// Stänger användarmenyn om man klickar utanför den.
document.addEventListener("click", (e) => {
  if (!userMenu.contains(e.target)) {
    userMenu.classList.remove("locked");
  }
});

// Öppnar/stänger genremenyn när man klickar på genreikonen.
genreIcon.addEventListener("click", (e) => {
  e.stopPropagation();
  genreMenu.classList.toggle("locked");
});

// Stänger genremenyn om man klickar utanför den.
document.addEventListener("click", (e) => {
  if (!genreMenu.contains(e.target)) {
    genreMenu.classList.remove("locked");
  }
});

// ==============================
// Inloggning
// ==============================

// Loggar in användaren när man klickar på login-knappen.
document.getElementById("login-btn").addEventListener("click", async () => {
  // Hämtar användarnamn och lösenord från inputfält.
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  // Skickar POST-förfrågan till servern för inloggning.
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // Skickar cookies.
    body: JSON.stringify({ username, password })
  });

  // Hanterar svaret från servern.
  const data = await res.json();
  if (res.ok) {
/**
 * Anger att användaren är inloggad och uppdaterar gränssnittet. 
 */
    isLoggedIn = true;
    document.getElementById("auth-status").textContent = "Logged in!";
    document.getElementById("logout-btn").style.display = "inline";
  } else {
    document.getElementById("auth-status").textContent = data.error;
  }
});

// ==============================
// Registrering
// ==============================

// Registrerar ny användare.
document.getElementById("register-btn").addEventListener("click", async () => {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  // Skickar POST-förfrågan till servern för att registrera.
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

// ==============================
// Utloggning
// ==============================

// Loggar ut användaren.
document.getElementById("logout-btn").addEventListener("click", async () => {
  await fetch(`${API_URL}/logout`, {
    method: "POST",
    credentials: "include"
  });
  isLoggedIn = false;
  document.getElementById("auth-status").textContent = "Logged out";
  document.getElementById("logout-btn").style.display = "none";
});

// ==============================
// Genrer
// ==============================

// Lista som lagrar alla tillgängliga genrer.
let genres = [];

/**
 * Hämtar en komplett lista över filmgenrer från TMDB och renderar dem i
 * sidopanelen.
 *
 * ### Flöde
 * 1. Anropa `/genre/movie/list` med aktuell `API_KEY`.  
 * 2. Extrahera `genres`‑arrayen ur svaret.  
 * 3. Spara till global variabel och anropa {@link displayGenres}.  
 *
 * @async
 * @throws `TypeError` om nätverksanropet misslyckas. Felet fångas lokalt och
 *   loggas till konsolen för att inte krascha appen.
 * @returns {Promise<void>} Löste när genrerna är färdigrenderade.
 *
 * @example
 * // Automatisk init i slutet av filen
 * fetchGenres();
 */
// Hämtar tillgängliga genrer från TMDb och visar dem.
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

/**
 * Skapar ett klickbart `<div>`‑element per genre och lägger till det i
 * `genrePanel`.
 *
 * Sid­effekt: Rensar panelen *innan* den fylls, så funktionen kan anropas flera
 * gånger (t.ex. efter en sökning) utan att skapa dubletter.
 *
 * @returns {void}
 */
// Visar alla genrer i menyfältet. 
function displayGenres() {
  genrePanel.innerHTML = ''; // Tömmer genrelistan först.

  // Skapar ett menyval för varje genre.
  genres.forEach((genre) => {
    const genreItem = document.createElement('div');
    genreItem.textContent = genre.name;
    genreItem.classList.add('genre-item');

    // När man klickar på en genre hämtas filmer i den genren.
    genreItem.addEventListener('click', () => {
      currentIndex = 0; 
      fetchMovies(40, genre.id);
    });

    genrePanel.appendChild(genreItem);
  });
}

/**
 * Hämtar ett godtyckligt antal sidor filmer via TMDB‑API:et.  
 * Standardläget (`genreId = null`) hämtar "mest populära" över alla genrer.
 * Med ett `genreId` filtrerar vi på angiven genre.
 *
 * ### Prestanda & begränsningar
 * • Varje sida = cirka 20 filmer.  
 * • 40 sidor ≈ 800 filmer ≈ ±10 MB JSON.  
 *   Detta är acceptabelt i en prototyp men kan justeras för produktion.  
 *
 * @async
 * @param {number} [pages=40]  Antal sidor att hämta.
 * @param {number|null} [genreId=null]  TMDB‑genre‑ID att filtrera på eller `null`.
 * @returns {Promise<void>}  När filmerna är hämtade och första kortet visas.
 *
 * @example
 * // Hämta 10 sidor actionfilmer (genre 28) och visa första kortet
 * fetchMovies(10, 28);
 */
// Hämtar populära filmer (eller filtrerat på genre).
async function fetchMovies(pages = 40, genreId = null) {
  const allMovies = [];

  // Går igenom varje sida för att hämta filmer.
  for (let i = 1; i <= pages; i++) {
    let url = `${BASE_URL}/movie/popular?api_key=${API_KEY}&language=en-US&page=${i}`;
    
    // Om genreId finns, hämtar bara filmer med den genren.
    if (genreId) {
      url = `${BASE_URL}/discover/movie?api_key=${API_KEY}&language=en-US&page=${i}&with_genres=${genreId}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    allMovies.push(...(data.results || []));
  }

  movies = shuffle(allMovies); // Blandar filmerna.
  showNextMovie(); // Visar första filmen.
}

/**
 * Renderar **`movies[currentIndex]`** som ett swipe‑kort. Om listan är slut
 * visas ett "Inga fler filmer"‑meddelande.
 *
 * @returns {void}
 */
// Visar nästa film i listan.
function showNextMovie() {
  if (currentIndex >= movies.length) {
    document.getElementById('movie-info').innerHTML = "<p>No more movies!</p>";
    container.innerHTML = '';
    return;
  }

  const movie = movies[currentIndex];
  const card = document.createElement('div');
  card.className = 'movie-card';

  // Använder TMDb-bild eller placeholder.
  const posterPath = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : 'https://via.placeholder.com/300x450?text=No+Image';

  // Visar betyg, datum och beskrivning.
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

/**
 * Binder mus‑ och touch‑händelser på ett filmkort för att känna av svep åt höger
 * (gilla) eller vänster (skip).
 *
 * ### Flöde
 * 1. **mousedown / touchstart**  → Spara start‑X.  
 * 2. **mousemove / touchmove**   → Flytta kortet och luta det proportionellt.  
 * 3. **mouseup / touchend**      → Om >50 px → gilla/skip, annars återställ.  
 *
 * @param {HTMLElement} card  Filmkortet som ska göras draggable.
 * @param {object}      movie Filmdata kopplad till kortet.
 * @returns {void}
 */
// Lägger till funktion för att dra kort åt höger/vänster. 
function addSwipeHandlers(card, movie) {
  let offsetX = 0;
  let isDragging = false;

  // Startar dragningen.
  const onDragStart = (e) => {
    isDragging = true;
    offsetX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
  };

  // Flyttar kortet medan man drar.
  const onDragMove = (e) => {
    if (!isDragging) return;
    const currentX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
    const diffX = currentX - offsetX;
    card.style.transform = `translateX(${diffX}px) rotate(${diffX / 20}deg)`;
  };

  // Avslutar dragningen och avgör riktning.
  const onDragEnd = (e) => {
    if (!isDragging) return;
    isDragging = false;
    const endX = e.type.includes('touch')
      ? e.changedTouches[0].clientX
      : e.clientX;
    const diffX = endX - offsetX;

    // Swipa höger = like, vänster = dislike.
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

  // Lägger till mus- och touchhändelser.
  card.addEventListener('mousedown', onDragStart);
  card.addEventListener('mousemove', onDragMove);
  card.addEventListener('mouseup', onDragEnd);
  card.addEventListener('touchstart', onDragStart);
  card.addEventListener('touchmove', onDragMove);
  card.addEventListener('touchend', onDragEnd);
}

/**
 * Animerar att kortet flyger åt vänster eller höger och laddar sen nästa film.
 *
 * @param {HTMLElement} card      Det kort som ska animeras bort.
 * @param {'left'|'right'} direction  "right" = gilla, "left" = skippa.
 * @returns {void}
 */
// Animerar kortet när det swipas bort. 
function animateSwipe(card, direction) {
  card.classList.add(direction === 'right' ? 'liked' : 'disliked');
  card.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
  card.style.transform = `translateX(${ direction === 'right' ? '500px' : '-500px' }) rotate(${ direction === 'right' ? '45deg' : '-45deg' })`;
  card.style.opacity = '0';

  // Vänta lite innan nästa film visas.
  setTimeout(() => {
    currentIndex++;
    showNextMovie();
  }, 400);
}

/**
 * Skickar filmens JSON till backend‑endpointen `/like` om användaren är inloggad.
 *
 * @param {object} movie  Film­objektet som användaren gillar.
 * @returns {void}
 */
// Skickar film till servern om användaren gillat den. 
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

/**
 * Stub för "skip"‑logik. Just nu loggas endast titeln till konsolen 
 *
 * @param {object} movie
 * @returns {void}
 */
// Skriver ut i konsolen när filmen ignoreras. 
function discardMovie(movie) {
  console.log("Discarded:", movie.title);
}

// ==============================
// Knappar för like/dislike
// ==============================

// Gillar filmen om man klickar på like-knappen.
likeBtn.addEventListener("click", () => {
  if (!currentCard) return;
  likeMovie(movies[currentIndex]);
  animateSwipe(currentCard, "right");
});

// Ignorerar filmen om man klickar på dislike-knappen.
dislikeBtn.addEventListener("click", () => {
  if (!currentCard) return;
  discardMovie(movies[currentIndex]);
  animateSwipe(currentCard, "left");
});

/**
 * Fisher‑Yates‑shuffle som blandar en array in‑place.
 *
 * @template T
 * @param {T[]} array  Arrayen som ska blandas.
 * @returns {T[]}      Samma array‑referens, nu i slumpad ordning.
 *
 * @example
 * const arr = [1, 2, 3, 4];
 * shuffle(arr); // t.ex. [3, 1, 4, 2]
 */
// Blandar om filmerna i listan. 
function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

// ==============================
// Initiering
// ==============================

// Hämtar genrer när sidan laddas.
fetchGenres();

// Hämtar filmer när sidan laddas.
fetchMovies();