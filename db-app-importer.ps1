$csvData = Import-Csv -Path "export.csv" -Encoding UTF8

# Select necessary columns from the file
$relevantData = $csvData | Select-Object Normal, Foil, Set, "Card Number"

# Type the exported data
$typedData = @()
foreach ($row in $relevantData) {
    $tempObj = [PSCustomObject] @{
        Normal = [int] $row.Normal
        Foil = [int] $row.Foil
        Set = [string] $row.Set.TrimStart("0")
        Number = [string] $row."Card Number".TrimStart("0")
    }
    $typedData += $tempObj
}

# Building a template hashtable
$h = [ordered]@{Wishlist=@(); OwnedCardQuantitiesV2=@(); Decks=@(); TutorialChapterStates=[ordered]@{WhatIsLorcana="Completed"; SettingUp="Completed"; PowerOfInk="Completed"; StartPlaying="Completed"; UsingCards="Completed"}; DisabledMaxSameCardsPerDeckPopup=[bool]0; PlayedIllumineerQuests=@("DeepTrouble"); }

$mapping = Import-Csv -Path "mapping.csv" -Encoding UTF8

$typedMapping = @()
foreach ($row in $mapping) {
    $tempObj = [PSCustomObject] @{
        Set = [string] $row.Set
        ID = [string] $row.ID
        Number = [string] $row."Card Number"
    }
    $typedMapping += $tempObj
}

# For each entry in the export it will look for the correctly mapped id
foreach ($row in $typedData) {
    $id = $typedMapping.Where({$_.Set -eq $row.Set -and $_.Number -eq $row.Number}).ID
    if ($null -eq $id) {
        Write-Output "ID not found for Set: $($row.Set), Number: $($row.Number)"
        continue
    } else {
        if ($row.Normal -gt 0) {
            $card = [ordered]@{Id=$id; Type="Regular"; Quantity=$row.Normal}
            $h.OwnedCardQuantitiesV2 += $card
        }
        if ($row.Foil -gt 0) {
            $card = [ordered]@{Id=$id; Type="Foiled"; Quantity=$row.Foil}
            $h.OwnedCardQuantitiesV2 += $card
        }
    }
}

$h | ConvertTo-Json | Out-File -FilePath "userdata.json" -Encoding UTF8 -Force
