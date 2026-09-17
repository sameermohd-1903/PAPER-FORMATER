"use strict";

document.addEventListener("DOMContentLoaded", function () {

    console.log("QUESTION ADD JS LOADED");

    const levelSelect = document.getElementById("id_level");
    const programSelect = document.getElementById("id_program");
    const semesterSelect = document.getElementById("id_semester");
    const subjectSelect = document.getElementById("id_subject");

    console.log("Level:", levelSelect);
    console.log("Program:", programSelect);
    console.log("Semester:", semesterSelect);
    console.log("Subject:", subjectSelect);

    console.log("Programs URL:", window.programsUrl);
    console.log("Semesters URL:", window.semestersUrl);
    console.log("Subjects URL:", window.subjectsUrl);


    // =========================================================
    // CHECK ELEMENTS
    // =========================================================

    if (!levelSelect || !programSelect || !semesterSelect || !subjectSelect) {
        console.error("One or more dropdowns were not found.");
        return;
    }


    // =========================================================
    // LOAD PROGRAMS
    // =========================================================

    async function loadPrograms(level) {

        console.log("Loading programs for level:", level);

        programSelect.innerHTML =
            '<option value="">Select Program</option>';

        semesterSelect.innerHTML =
            '<option value="">Select Semester</option>';

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!level) {
            return;
        }

        try {

            const url =
                `${window.programsUrl}?level=${encodeURIComponent(level)}`;

            console.log("Fetching:", url);

            const response = await fetch(url);

            console.log("Program response:", response.status);

            if (!response.ok) {
                throw new Error(
                    `Program request failed: ${response.status}`
                );
            }

            const programs = await response.json();

            console.log("Programs received:", programs);

            programs.forEach(function (program) {

                const option =
                    document.createElement("option");

                option.value = program.id;
                option.textContent = program.name;

                programSelect.appendChild(option);
            });

        } catch (error) {

            console.error(
                "Program loading error:",
                error
            );
        }
    }


    // =========================================================
    // LEVEL → PROGRAM
    // =========================================================

    levelSelect.addEventListener("change", function () {

        loadPrograms(this.value);

    });


    // =========================================================
    // LOAD PROGRAMS WHEN PAGE OPENS
    // =========================================================

    if (levelSelect.value) {

        loadPrograms(levelSelect.value);

    }


    // =========================================================
    // PROGRAM → SEMESTER
    // =========================================================

    programSelect.addEventListener("change", async function () {

        const programId = this.value;

        console.log("Selected program:", programId);

        semesterSelect.innerHTML =
            '<option value="">Select Semester</option>';

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!programId) {
            return;
        }

        try {

            const response = await fetch(
                `${window.semestersUrl}?program=${encodeURIComponent(programId)}`
            );

            if (!response.ok) {
                throw new Error(
                    `Semester request failed: ${response.status}`
                );
            }

            const semesters = await response.json();

            console.log("Semesters received:", semesters);

            semesters.forEach(function (semester) {

                const option =
                    document.createElement("option");

                option.value = semester.id;

                option.textContent =
                    `Semester ${semester.number}`;

                semesterSelect.appendChild(option);

            });

        } catch (error) {

            console.error(
                "Semester loading error:",
                error
            );
        }
    });


    // =========================================================
    // SEMESTER → SUBJECT
    // =========================================================

    semesterSelect.addEventListener("change", async function () {

        const semesterId = this.value;
        const programId = programSelect.value;

        console.log(
            "Selected program:",
            programId,
            "Selected semester:",
            semesterId
        );

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!programId || !semesterId) {
            return;
        }

        try {

            const response = await fetch(
                `${window.subjectsUrl}?program=${encodeURIComponent(programId)}&semester=${encodeURIComponent(semesterId)}`
            );

            if (!response.ok) {
                throw new Error(
                    `Subject request failed: ${response.status}`
                );
            }

            const subjects = await response.json();

            console.log("Subjects received:", subjects);

            subjects.forEach(function (subject) {

                const option =
                    document.createElement("option");

                option.value = subject.id;
                option.textContent = subject.name;

                subjectSelect.appendChild(option);

            });

        } catch (error) {

            console.error(
                "Subject loading error:",
                error
            );
        }
    });

});