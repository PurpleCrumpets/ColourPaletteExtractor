# ColourPaletteExtractor is a simple tool to generate the colour palette of an image.
# Copyright (C) 2021  Tim Churchfield
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


#----------
# Simple script to replace a pattern with a new string in the given file

# Example usage PowerShell.exe -ExecutionPolicy Bypass -File %FIND_AND_REPLACE% %FILE_NAME% %PATTERN% %REPLACEMENT%
#----------

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
