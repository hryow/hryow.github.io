document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('#navbar-links a').forEach((link) => {
        const linkPage = link.getAttribute('href').split('/').pop();
        if (linkPage === currentPage) {
            link.setAttribute('aria-current', 'page');
        }
    });

    const myButton = document.getElementById('myBtn');

    if (myButton) {
        const scrollFunction = () => {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                myButton.style.display = 'block';
            } else {
                myButton.style.display = 'none';
            }
        };

        window.addEventListener('scroll', scrollFunction, { passive: true });
        myButton.addEventListener('click', () => {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        });
        scrollFunction();
    }

    const contactForm = document.getElementById('contactForm');

    if (contactForm) {
        contactForm.addEventListener('submit', (event) => {
            event.preventDefault();

            const errorElements = contactForm.querySelectorAll('.error-message');
            errorElements.forEach((element) => {
                element.style.display = 'none';
                element.textContent = '';
            });

            const name = contactForm.querySelector('#contact-name').value.trim();
            const email = contactForm.querySelector('#email').value.trim();
            const phone = contactForm.querySelector('#phone').value.trim();
            const message = contactForm.querySelector('#message').value.trim();

            let isValid = true;

            if (name === '') {
                contactForm.querySelector('#nameError').textContent = 'Name is required';
                contactForm.querySelector('#nameError').style.display = 'block';
                isValid = false;
            }

            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (email === '' || !emailPattern.test(email)) {
                contactForm.querySelector('#emailError').textContent = 'Valid email is required';
                contactForm.querySelector('#emailError').style.display = 'block';
                isValid = false;
            }

            const phoneDigits = phone.replace(/\D/g, '');
            if (phone === '' || phoneDigits.length < 10 || phoneDigits.length > 15) {
                contactForm.querySelector('#phoneError').textContent = 'Valid phone number is required';
                contactForm.querySelector('#phoneError').style.display = 'block';
                isValid = false;
            }

            if (message === '') {
                contactForm.querySelector('#messageError').textContent = 'Message is required';
                contactForm.querySelector('#messageError').style.display = 'block';
                isValid = false;
            }

            if (isValid) {
                const subject = encodeURIComponent(`Portfolio contact from ${name}`);
                const body = encodeURIComponent(
                    `Name: ${name}\nEmail: ${email}\nPhone: ${phone}\n\n${message}`,
                );
                window.location.href = `mailto:hayoung.ryow@gmail.com?subject=${subject}&body=${body}`;
                contactForm.querySelector('#formStatus').textContent =
                    'Your email app should open with the message ready to send.';
            }
        });
    }

    const projectsRoot = document.getElementById('projects');

    if (projectsRoot) {
        fetch('./data/projects.json')
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Unable to load project data: ${response.status}`);
                }

                return response.json();
            })
            .then((projects) => {
                projectsRoot.innerHTML = projects
                    .map((project) => `
                        <article data-tag="${project.tags.join(' ')}">
                            <div class="bg-rectangle" style="background-color: ${project.background}">
                                ${project.placeholder
                                    ? `<div class="project-placeholder" role="img" aria-label="${project.title} project preview coming soon">project preview<br><span>coming soon</span></div>`
                                    : `<img ${project.imageClass ? `class="${project.imageClass}"` : ''} src="${project.image}" alt="${project.title}" loading="lazy" decoding="async" ${project.imageWidth ? `width="${project.imageWidth}"` : ''}>`}
                            </div>
                            <div class="proj-desc">
                                <p class="heading"><strong><span>${project.category}</span></strong></p>
                                <h3>${project.title}</h3>
                                <p class="heading"><em>${project.date}</em><br><span>${project.stack.join(', ')}</span></p>
                                <p>${project.summary}</p>
                                <a class="button" href="${project.link}">${project.linkLabel}</a>
                                <br>
                            </div>
                        </article>
                    `)
                    .join('');

                const buttons = Array.from(document.querySelectorAll('#sort .tag'));
                const articles = Array.from(document.querySelectorAll('#projects article'));

                const applyFilter = (tag) => {
                    buttons.forEach((button) => button.classList.remove('active'));
                    buttons.forEach((button) => {
                        button.setAttribute('aria-pressed', 'false');
                    });

                    const activeButton = buttons.find((button) => button.getAttribute('data-tag') === tag);
                    if (activeButton) {
                        activeButton.classList.add('active');
                        activeButton.setAttribute('aria-pressed', 'true');
                    }

                    articles.forEach((article) => {
                        const selectedTags = article.getAttribute('data-tag').split(' ');
                        article.style.display = selectedTags.includes(tag) || tag === 'all' ? '' : 'none';
                    });
                };

                applyFilter('all');

                buttons.forEach((button) => {
                    button.addEventListener('click', () => {
                        applyFilter(button.getAttribute('data-tag'));
                    });
                });
            })
            .catch((error) => {
                projectsRoot.innerHTML = `<p class="resume-error">${error.message}</p>`;
            });
    }

    const resumeRoot = document.getElementById('resume-root');

    if (resumeRoot) {
        fetch('./data/resume.json')
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Unable to load resume data: ${response.status}`);
                }

                return response.json();
            })
            .then((resume) => {
                document.title = `${resume.basics.name} | Resume`;

                const sectionHtml = (title, content) => `
                    <section class="resume-section">
                        <h2>${title}</h2>
                        ${content}
                    </section>
                `;

                const bullets = (items) => `
                    <ul class="resume-bullets">
                        ${items.map((item) => `<li>${item}</li>`).join('')}
                    </ul>
                `;

                const experienceHtml = resume.experience.map((entry) => `
                    <article class="resume-entry">
                        <div class="resume-entry-header">
                            <div>
                                <h3>${entry.company}</h3>
                                <p class="resume-role">${entry.title}</p>
                                <p class="resume-meta">${entry.tools.join(' · ')}</p>
                            </div>
                            <div class="resume-meta resume-meta-right">
                                <p>${entry.location}</p>
                                <p>${entry.start} - ${entry.end}</p>
                            </div>
                        </div>
                        ${bullets(entry.highlights)}
                    </article>
                `).join('');

                const projectHtml = resume.projects.map((project) => `
                    <article class="resume-entry resume-project">
                        <div class="resume-entry-header">
                            <div>
                                <h3>${project.name}</h3>
                                <p class="resume-role">${project.category}</p>
                                <p class="resume-meta">${project.stack.join(' · ')}</p>
                            </div>
                            <div class="resume-meta resume-meta-right">
                                <p>${project.date}</p>
                            </div>
                        </div>
                        <p>${project.summary}</p>
                    </article>
                `).join('');

                const educationHtml = resume.education.map((entry) => `
                    <article class="resume-entry">
                        <div class="resume-entry-header">
                            <div>
                                <h3>${entry.school}</h3>
                                <p class="resume-role">${entry.degree}</p>
                                <p class="resume-meta">${entry.coursework}</p>
                            </div>
                            <div class="resume-meta resume-meta-right">
                                <p>${entry.location}</p>
                                <p>${entry.dates}</p>
                            </div>
                        </div>
                        ${bullets(entry.highlights)}
                    </article>
                `).join('');

                const leadershipHtml = bullets(resume.leadership.map((item) => `<strong>${item.role}</strong> of ${item.organization} <span>${item.dates}</span>`));

                resumeRoot.innerHTML = `
                    <header class="resume-header">
                        <div>
                            <p class="resume-kicker">${resume.basics.location}</p>
                            <h1>${resume.basics.name}</h1>
                            <p class="resume-summary">${resume.summary}</p>
                        </div>
                        <div class="resume-actions">
                            <a class="button" href="${resume.pdfPath}" target="_blank" rel="noreferrer">+ download pdf +</a>
                            <a class="button button-secondary" href="${resume.basics.website}" target="_blank" rel="noreferrer">+ website +</a>
                        </div>
                        <div class="resume-links">
                            <a href="mailto:${resume.basics.email}">${resume.basics.email}</a>
                            <a href="${resume.basics.linkedin}" target="_blank" rel="noreferrer">linkedin</a>
                            <a href="${resume.basics.github}" target="_blank" rel="noreferrer">github</a>
                        </div>
                    </header>

                    ${sectionHtml('skills', `
                        <div class="resume-skill-grid">
                            ${resume.skills.map((skillGroup) => `
                                <div class="resume-skill-card">
                                    <h3>${skillGroup.category}</h3>
                                    <p>${skillGroup.items.join(', ')}</p>
                                </div>
                            `).join('')}
                        </div>
                    `)}

                    ${sectionHtml('experience', experienceHtml)}
                    ${sectionHtml('selected projects', projectHtml)}
                    ${sectionHtml('education', educationHtml)}
                    ${sectionHtml('leadership', leadershipHtml)}
                `;
            })
            .catch((error) => {
                resumeRoot.innerHTML = `<p class="resume-error">${error.message}</p>`;
            });
    }
});