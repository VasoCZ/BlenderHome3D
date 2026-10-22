Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile("C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_overview.png")
$w = $img.Width
$h = $img.Height

# Crop the patio and facade lights on the bottom and right
$r1 = [System.Drawing.Rectangle]::new([int]($w * 0.45), [int]($h * 0.45), [int]($w * 0.35), [int]($h * 0.40))
$bmp1 = New-Object System.Drawing.Bitmap $r1.Width, $r1.Height
$g1 = [System.Drawing.Graphics]::FromImage($bmp1)
$g1.DrawImage($img, 0, 0, $r1, [System.Drawing.GraphicsUnit]::Pixel)
$bmp1.Save("C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\detail_facade_lights.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g1.Dispose()
$bmp1.Dispose()

# Crop the south wall lights
$r2 = [System.Drawing.Rectangle]::new([int]($w * 0.10), [int]($h * 0.30), [int]($w * 0.30), [int]($h * 0.35))
$bmp2 = New-Object System.Drawing.Bitmap $r2.Width, $r2.Height
$g2 = [System.Drawing.Graphics]::FromImage($bmp2)
$g2.DrawImage($img, 0, 0, $r2, [System.Drawing.GraphicsUnit]::Pixel)
$bmp2.Save("C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\detail_front_lights.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g2.Dispose()
$bmp2.Dispose()

$img.Dispose()
Write-Host "Crops saved."
