# Input Arguments
$file = $args[0] # File
$pattern = $args[1] # Pattern
$replacement = $args[2] # Replacement

# Print input arguments to the terminal
write-host ""
write-host $file
write-host $pattern
write-host $replacement

# Find and replace
(Get-Content $file) -replace $pattern, $REPLACEMENT | Out-File $file -Encoding utf8
