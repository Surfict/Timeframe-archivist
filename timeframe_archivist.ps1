param(
    [string]$day, # Expected format: YYYY-MM-DD
    [string]$event_start, # Expected format: HH:mm
    [string]$event_stop, # Expected format: HH:mm
    [string]$event_timezone, # Timezone of the event times
    [string]$command, # Command to be executed - can be list_videos, copy_files or delete_files
    [string]$files_destination_path # Copy files to the given directory
)

function List-Videos {
    param(
        [string]$day,
        [string]$event_start,
        [string]$event_stop,
        [object]$SourceFolder,
        [string]$EventTimezone
    )

    $filteredFiles = @()

    # Create DateTime objects in the event timezone and convert to local timezone
    $eventTimeZoneInfo = [TimeZoneInfo]::FindSystemTimeZoneById($event_timezone)
    $localTimeZoneInfo = [TimeZoneInfo]::Local

    $startDateTimeUTC = [TimeZoneInfo]::ConvertTimeToUtc(
        [DateTime]::ParseExact("$day $event_start", "dd/MM/yyyy HH:mm", $null), 
        $eventTimeZoneInfo
    )

    $endDateTimeUTC = [TimeZoneInfo]::ConvertTimeToUtc(
        [DateTime]::ParseExact("$day $event_stop", "dd/MM/yyyy HH:mm", $null), 
        $eventTimeZoneInfo
    )



    $yearMonth = $day.Substring(5,5).Replace("/","") + $day.Substring(2,4).Replace("/","") # Extract YYYYMM format
    # Filter folders that start with YYYYMM
    $test = $SourceFolder.Items()
    $folders = $SourceFolder.Items() | Where-Object { $_.IsFolder -and $_.Name.StartsWith($yearMonth) }

    foreach ($folder in $folders) {
		#$a = $folder.Name
        $items = $folder.GetFolder.Items() | Where-Object { ($_.Name -like "*.mp4" -or $_.Name -like "*.MOV") }
        foreach ($item in $items) {
            $itemCreationTimeUTC = $item.ExtendedProperty("System.DateCreated")
			$modifieddate = $itemCreationTime
            
            if ($itemCreationTimeUTC -ge $startDateTimeUTC -and $itemCreationTimeUTC -le $endDateTimeUTC) {
                $filteredFiles += $item
            }
        }
    }



    # Display or further process the filtered files
  #  $filteredFiles | ForEach-Object {
  #      $size = [math]::round($($_.ExtendedProperty("System.Size")) /1Mb, 0)
  #      Write-Host "Filtered file:  $size MB"
  #      Write-Host "Filtered file:  $($_.ExtendedProperty("System.Size"))"
  #      #Write-Host "Filtered file:  $($_.Name)"
  #  }

    return $filteredFiles
}

$phoneRelativePath = 'Internal Storage'
$shell  = New-Object -com shell.application
$PhoneFolder = ($shell.NameSpace("shell:MyComputerFolder").Items() | where Type -match 'Mobile Phone|Portable Device').GetFolder

# Check if the iphone is connected
if ($null -eq $PhoneFolder) {
    return '{"Error" : "Iphone not found. Check that it is correctly plugged in your machine."}' | ConvertTo-Json
}

$SourceFolder = ($PhoneFolder.Items() | where {$_.IsFolder} | where Name -eq $phoneRelativePath).GetFolder

$filteredVideos = List-Videos -day $day -event_start $event_start -event_stop $event_stop -SourceFolder $SourceFolder -EventTimezone $event_timezone

if ($command -eq "list_videos") {
    $videoList = @()
    foreach ($video in $filteredVideos) {
        $sizeMB = [math]::round($video.ExtendedProperty("System.Size") / 1MB, 0)
        $creationDate = $video.ExtendedProperty("System.DateCreated")
        $creationDateTime = [DateTime]$creationDate
        #$formattedCreationDate = $creationDate.ToString("dd/MM/yyyy HH:mm")
        # Define the target timezone
        $targetTimeZone = [TimeZoneInfo]::FindSystemTimeZoneById($event_timezone)
        
        # Convert local DateTime to the target timezone
        $creationDateTargetTZ = [TimeZoneInfo]::ConvertTime($creationDateTime, [TimeZoneInfo]::UTC, $targetTimeZone)
        
        # Format the DateTime to string in the target timezone
        $formattedCreationDateTargetTZ = $creationDateTargetTZ.ToString("dd/MM/yyyy HH:mm")
        $videoObject = [PSCustomObject]@{
            Name = $video.Name
            SizeMB = "$sizeMB"
            CreationDate = $formattedCreationDateTargetTZ
        }
        $videoList += $videoObject
    }

    if ($videoList.Count -eq 0) {
        return "[]"
    } elseif ($videoList.Count -eq 1) {
        $json_videoList = $videoList | ConvertTo-Json 
        return "[" + $json_videoList + "]"
    }
    else{
        return $videoList | ConvertTo-Json
    }
    
    
}

elseif ($command -eq "copy_files") {

    $totalItems = $filteredVideos.count
    if ($totalItems -gt 0)
    {
        # If destination path doesn't exist, create it only if we have some items to move
        if (-not (test-path $files_destination_path) )
        {
            $created = new-item -itemtype directory -path $files_destination_path
        }
 
        $destinationFolder = $shell.Namespace($files_destination_path).self
        foreach ($item in $filteredVideos)
        {
            $fileName = $item.Name
 
            # Check the target file doesn't exist:
            $targetFilePath = join-path -path $files_destination_path -childPath $fileName
            if (test-path -path $targetFilePath)
            {
                    $errorMessage = "Destination file exists - file $($item.Name) not moved to :`n`t$targetFilePath"
                    $errorObject = @{ Error = $errorMessage }
                    return $errorObject | ConvertTo-Json
            }
            else
            {
                $destinationFolder.GetFolder.CopyHere($item)
                if (test-path -path $targetFilePath)
                {
                    
                }
                else
                {
                    $errorMessage = "Failed to move file $($item.Name) to destination:`n`t$targetFilePath"
                    $errorObject = @{ Error = $errorMessage }
                    return $errorObject | ConvertTo-Json
                }
            }
        }
    }
    return '{"Result" "Success"}' | ConvertTo-Json

}

elseif ($command -eq "delete_files") {
    Write-Host "delete_files"

}
# Case 
else {
    Write-Error "Command parameter is incorrect. It has to be choosen from : 'list_videos, copy_files, delete_files'"
    return $false
}