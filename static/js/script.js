document.addEventListener("DOMContentLoaded", () => {
    console.log("JavaScript Loaded!");

    // Modal functionality
    const modals = document.querySelectorAll(".modal");
    const modalTriggers = document.querySelectorAll("[data-modal-target]");
    const closeButtons = document.querySelectorAll(".modal-close");

    modalTriggers.forEach(trigger => {
        trigger.addEventListener("click", () => {
            const target = trigger.getAttribute("data-modal-target");
            const modal = document.querySelector(target);
            openModal(modal);
        });
    });

    closeButtons.forEach(button => {
        button.addEventListener("click", () => {
            const modal = button.closest(".modal");
            closeModal(modal);
        });
    });

    function openModal(modal) {
        if (modal) {
            modal.classList.add("active");
            document.body.style.overflow = "hidden"; // Prevent background scroll
        }
    }

    function closeModal(modal) {
        if (modal) {
            modal.classList.remove("active");
            document.body.style.overflow = ""; // Restore background scroll
        }
    }

    // Click outside modal to close
    modals.forEach(modal => {
        modal.addEventListener("click", event => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    // Form Validation
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", event => {
            const inputs = form.querySelectorAll("input, textarea");
            let valid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.classList.add("error");
                    showError(input, "This field is required.");
                } else {
                    input.classList.remove("error");
                    clearError(input);
                }
            });

            if (!valid) {
                event.preventDefault();
                console.warn("Form validation failed!");
            }
        });
    });

    function showError(input, message) {
        const errorText = document.createElement("span");
        errorText.className = "error-text";
        errorText.textContent = message;
        if (!input.nextElementSibling || !input.nextElementSibling.classList.contains("error-text")) {
            input.insertAdjacentElement("afterend", errorText);
        }
    }

    function clearError(input) {
        const errorText = input.nextElementSibling;
        if (errorText && errorText.classList.contains("error-text")) {
            errorText.remove();
        }
    }

    // Smooth Scroll
    const scrollLinks = document.querySelectorAll('a[href^="#"]');
    scrollLinks.forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            const targetId = link.getAttribute("href").substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop,
                    behavior: "smooth"
                });
            }
        });
    });

    // Button Ripple Effect
    const buttons = document.querySelectorAll("button");
    buttons.forEach(button => {
        button.addEventListener("click", event => {
            const x = event.clientX - button.offsetLeft;
            const y = event.clientY - button.offsetTop;

            const ripple = document.createElement("span");
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.className = "ripple";

            button.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600); // Ripple effect duration
        });
    });
});
