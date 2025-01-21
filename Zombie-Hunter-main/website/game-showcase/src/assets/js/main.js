document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('dark-mode'); // Start in dark mode

    const galleryButton = document.getElementById('gallery-button');
    const galleryContainer = document.querySelector('.gallery-container');
    const galleryText = document.querySelector('.gallery-text');
    const images = document.querySelectorAll('.gallery img');
    const descriptions = [
        "Revolver: A reliable sidearm with good accuracy.",
        "Shotgun: A close-range weapon with a wide spread.",
        "Assault Rifle: A versatile weapon with high fire rate.",
        "Grenade: A powerful explosive device.",
        "Shield: Provides protection against attacks.",
        "Medkit: Restores health when used.",
        "2x Points: Doubles the points earned for a limited time.",
        "Freeze Zombies: Temporarily freezes all zombies.",
        "Infinite Ammo: Grants unlimited ammunition for a short period.",
        "Instant Kill: Allows one-hit kills for a limited time."
    ];
    const descriptionTitle = document.getElementById('description-title');
    const descriptionText = document.getElementById('description-text');
    let currentIndex = 0;

    const instructions = document.createElement('div');
    instructions.id = 'instructions';
    instructions.textContent = 'Use A and D keys to navigate';
    document.body.appendChild(instructions);

    function updateGallery() {
        images.forEach((img, index) => {
            img.style.display = index === currentIndex ? 'block' : 'none';
        });
        descriptionTitle.textContent = images[currentIndex].alt;
        descriptionText.textContent = descriptions[currentIndex];
    }

    galleryButton.addEventListener('click', () => {
        galleryText.style.opacity = '0';
        setTimeout(() => {
            galleryText.style.display = 'none';
            galleryContainer.style.transform = 'scale(1)';
            instructions.style.display = 'block';
            updateGallery(); // Ensure gallery is updated when opened
        }, 1000);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'A' || event.key === 'a') {
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : images.length - 1;
            updateGallery();
        } else if (event.key === 'D' || event.key === 'd') {
            currentIndex = (currentIndex < images.length - 1) ? currentIndex + 1 : 0;
            updateGallery();
        }
    });

    updateGallery();

    const b1 = new OnOffButton("#btn1");
    const b2 = new OnOffButton("#btn2");

    class OnOffButton {
        constructor(el) {
            this.el = document.querySelector(el);
            this.el?.addEventListener("click", this.power.bind(this));
        }
        power() {
            const pressed = this.el?.getAttribute("aria-pressed") === "true";
            this.el?.setAttribute("aria-pressed", `${!pressed}`);
            document.body.classList.toggle('dark-mode', !pressed);
        }
    }

    const modeToggleButton = document.getElementById('mode-toggle');
    function updateModeButtonText() {
        if (document.body.classList.contains('dark-mode')) {
            modeToggleButton.textContent = 'Light Mode?';
            descriptionText.style.color = 'white';
        } else {
            modeToggleButton.textContent = 'Dark Mode?';
            descriptionText.style.color = 'black';
        }
    }

    modeToggleButton.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        document.body.classList.toggle('dark-mode');
        updateModeButtonText();
    });

    updateModeButtonText();

    // Add a new section to showcase the game
    const showcaseSection = document.createElement('section');
    showcaseSection.id = 'game-showcase';
    showcaseSection.innerHTML = `
        <h2>Game Features</h2>
        <ul class="feature-list">
            <li>Intense zombie battles</li>
            <li>Wide variety of weapons</li>
            <li>Challenging levels</li>
            <li>Stunning graphics</li>
            <li>Engaging storyline</li>
        </ul>
        <div class="code-section">
            <div class="code-description">
                <h3>Grenade Timer</h3>
                <pre>
class Grenade {
    constructor(x, y, timer=2) {
        this.x = x;
        this.y = y;
        this.timer = timer;
        // ...existing code...
    }
    // ...existing code...
}
                </pre>
            </div>
            <div class="code-image">
                <img src="assets/images/grenade_timer.png" alt="Grenade Timer">
            </div>
        </div>
    `;
    document.body.appendChild(showcaseSection);

    // Add hover effect to change text color to red
    document.querySelectorAll('h1, h2, .gallery-text, #description-title, #description-text, .feature-list li').forEach(element => {
        element.addEventListener('mouseover', () => {
            element.style.color = 'red';
        });
        element.addEventListener('mouseout', () => {
            element.style.color = ''; // Reset to default color
        });
    });

    // Ensure background music starts playing and resumes from the last position
    const backgroundMusic = document.getElementById('background-music');
    if (sessionStorage.getItem('backgroundMusicTime')) {
        backgroundMusic.currentTime = sessionStorage.getItem('backgroundMusicTime');
    }
    backgroundMusic.play();

    window.addEventListener('beforeunload', () => {
        sessionStorage.setItem('backgroundMusicTime', backgroundMusic.currentTime);
    });
});
