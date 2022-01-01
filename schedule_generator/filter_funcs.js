function getLowerLevel(teamName) {
  const numTeamsPerLevel = {
    "REC": 1,
    "INT": 1,
    "COM": 1,
    "POW": 1,
    "P+": 1
  };
  const levelBelowMapping = {
    "INT": "REC",
    "COM": "INT",
    "POW": "COM",
    "P+": "POW"
  };
  const levelClsNames = {
    "REC": "rec",
    "INT": "int",
    "COM": "com",
    "POW": "pow",
    "P+": "pow_plus"
  };
  for (const level in levelBelowMapping) {
    if (teamName.startsWith(level)) {
      const lowerLevel = levelBelowMapping[level];
      const numTeams = numTeamsPerLevel[lowerLevel];
      let lowerLevelTeams = [];
      for (let i = 1; i <= numTeams; i++) {
        lowerLevelTeams.push(lowerLevel + i.toString());
      }
      return {"teams": lowerLevelTeams, "clsName": levelClsNames[lowerLevel]};
    }
  }
  // If we reached the end of the for loop without finding anything, return empty list
  return {"teams": [], "clsName": ""};
}

function showAll() {
  // Get the schedule table element and it's rows
  let table = document.getElementById("myTable");
  let tr = table.getElementsByTagName("tr");
  // Reset all hidden/highlighted rows/cols to make sure everything is shown
  for (let row = 0; row < tr.length; row++) {
    tr[row].style.display = "";
    let td = tr[row].getElementsByTagName("td");
    for (let col = 0; col < td.length; col++) {
      if (td[col].classList.contains("highlighted")) {
        td[col].classList.remove("highlighted");
      }
      if (td[col].classList.contains("hidden")) {
        td[col].classList.remove("hidden");
      }
      if (td[col].classList.contains("bye_hidden")) {
        td[col].classList.remove("bye_hidden");
      }
    }
  }
}

// NOTE: We assume all of the params passed in are defined!
function filterSchedule(firstTeam, secondTeam, showOpenPlay, showSkillsClinic) {
  // If SHOWALL is selected, just call showAll and exit early
  if (firstTeam == "SHOWALL") {
    showAll();
    return;
  }

  // Get the schedule table element and it's rows and iterate over them
  let table = document.getElementById("myTable");
  let tr = table.getElementsByTagName("tr");
  for (let row = 0; row < tr.length; row++) {
    // First check for row types that are always shown
    const trClass = tr[row].className;
    if (trClass == "header" || trClass == "week" || trClass == "spacer") {
      // Since we never hide these rows, we don't need to unhide them either... just skip
      continue;
    }
    // Next see if this row contains any mention of the selected filters
    // For regular rows, we also need to keep track of what surrounding cols were in the same court
    let highlightCols = [];
    let displayCols = [];
    let td = tr[row].getElementsByTagName("td");
    // NOTE: We ignore column 0 (time column) because it's always shown and never highlighted
    for (let col = 1; col < td.length; col++) {
      if (td[col]) {
        // We only care about team/bye/open_play/skills_clinic columns so ignore the rest
        const clsList = td[col].classList;
        const tdValue = td[col].textContent.toUpperCase();
        if (clsList.contains("team1")) {
          if (tdValue == firstTeam || tdValue == secondTeam) {
            highlightCols.push(col);
            displayCols.push(col, col + 1, col + 2, col + 3, col + 4);
          }
        } else if (clsList.contains("team2")) {
          if (tdValue == firstTeam || tdValue == secondTeam) {
            highlightCols.push(col);
            displayCols.push(col + -2, col - 1, col, col + 1, col + 2);
          }
        } else if (clsList.contains("team_ref")) {
          if (tdValue == firstTeam || tdValue == secondTeam) {
            highlightCols.push(col - 1, col);
            displayCols.push(col - 4, col - 3, col + -2, col - 1, col);
          }
        } else if (clsList.contains("bye")) {
          if (tdValue == firstTeam || tdValue == secondTeam) {
            highlightCols.push(col);
            displayCols.push(col);
          }
        } else {
          // Lastly check for open play and skills clinic cols
          if ((clsList.contains("open_play") && showOpenPlay) ||
              (clsList.contains("skills_clinic") && showSkillsClinic)) {
            displayCols.push(col);
          }
        }
      }
    }
    // If displayCols is empty we can just hide the whole row
    if (displayCols.length == 0) {
      tr[row].style.display = "none";
    } else {
      // Make sure this row is unhidden in case it was previously hidden
      tr[row].style.display = "";
      // Now we can set or unset the hidden/highlighted classes for each col
      // NOTE: We ignore column 0 (time column) because it's always shown and never highlighted
      for (let col = 1; col < td.length; col++) {
        // Highlight column if necessary
        if (highlightCols.includes(col)) {
          if (!td[col].classList.contains("highlighted")) {
            td[col].classList.add("highlighted");
          }
        } else if (td[col].classList.contains("highlighted")) {
          // Remove highlighting if previously highlighted
          td[col].classList.remove("highlighted");
        }
        // For hiding/displaying cols, we need to know if it's a bye week row
        const isByeWeekRow = (td[0].textContent == "Bye Week");
        const hiddenClsName = isByeWeekRow ? "bye_hidden" : "hidden";
        if (displayCols.includes(col)) {
          // Unhide this col if necessary
          if (td[col].classList.contains(hiddenClsName)) {
            td[col].classList.remove(hiddenClsName);
          }
        } else if (!td[col].classList.contains(hiddenClsName)) {
          // Make sure this col is hidden
          td[col].classList.add(hiddenClsName);
        }
      }
    }
  }
}

function handleOptionalFiltersChange() {
  // Get all of the filter values
  const firstTeam = document.getElementById("firstTeamSelect").value;
  const secondTeam = document.getElementById("secondTeamSelect").value;
  const showOpenPlay = document.getElementById("showOpenPlay").checked;
  const showSkillsClinic = document.getElementById("showSkillsClinic").checked;
  return filterSchedule(firstTeam, secondTeam, showOpenPlay, showSkillsClinic);
}

function handleFirstTeamSelectChange() {
  // First check what team was selected from the firstTeamSelect dropdown
  const filteredTeam = document.getElementById("firstTeamSelect").value.toUpperCase();

  // Get handles for all the optional filter elements that we need to control
  let optionalFiltersDiv = document.getElementById("optional_filters_div");
  let secondTeamSelect = document.getElementById("secondTeamSelect")
  let showOpenPlay = document.getElementById("showOpenPlay");
  let showSkillsClinic = document.getElementById("showSkillsClinic");

  // Any change to the first team selection should reset second team selection options
  while (secondTeamSelect.options.length) {
    secondTeamSelect.remove(0);
  }

  // If the filter is set to SHOWALL disable optional filters and reset their values
  if (filteredTeam == "SHOWALL") {
    secondTeamSelect.disabled = true;
    showOpenPlay.checked = false;
    showOpenPlay.disabled = true;
    showSkillsClinic.checked = false;
    showSkillsClinic.disabled = true;
    optionalFiltersDiv.style.display = "none";
  } else {
    // Enable optional filters
    optionalFiltersDiv.style.display = "table";
    showOpenPlay.disabled = false;
    showSkillsClinic.disabled = false;
    // Check if there are lower level teams to populate the second team selection drop down
    const lowerLevel = getLowerLevel(filteredTeam);
    // If there are no lower level teams, disable the selection
    if (lowerLevel.teams.length == 0) {
      secondTeamSelect.disabled = true;
    } else {
      secondTeamSelect.disabled = false;
      // Populate select values for second team (first add default empty selection)
      let empty_opt = document.createElement("option");
      empty_opt.disabled = true;
      empty_opt.value = "";
      empty_opt.selected = true;
      secondTeamSelect.add(empty_opt);
      for (const team of lowerLevel.teams) {
        let opt = document.createElement("option");
        opt.value = opt.text = team;
        opt.classList.add(lowerLevel.clsName);
        secondTeamSelect.add(opt);
      }
    }
  }
  // Finally filter the schedule based on the first team selection
  return filterSchedule(filteredTeam, "", showOpenPlay.checked, showSkillsClinic.checked);
}