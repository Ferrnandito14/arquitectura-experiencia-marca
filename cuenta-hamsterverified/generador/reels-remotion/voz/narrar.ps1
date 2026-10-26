# Graba cada línea de un archivo de texto (una frase por línea, UTF-8) con la voz
# "Microsoft Pablo" de Windows y deja l0.wav, l1.wav, ... en la carpeta de salida.
# Uso: powershell -NoProfile -File narrar.ps1 -Lineas lineas.txt -Salida carpeta
param(
  [Parameter(Mandatory = $true)][string]$Lineas,
  [Parameter(Mandatory = $true)][string]$Salida,
  [string]$Voz = 'Microsoft Pablo',
  [double]$Velocidad = 1.05
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.DataReader, Windows.Storage.Streams, ContentType = WindowsRuntime]

$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Esperar($op, [Type]$tipo) {
  $t = $asTask.MakeGenericMethod($tipo).Invoke($null, @($op))
  $t.Wait() | Out-Null
  $t.Result
}

$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$elegida = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.DisplayName -eq $Voz }
if (-not $elegida) { throw "No está instalada la voz '$Voz'." }
$synth.Voice = $elegida
$synth.Options.SpeakingRate = $Velocidad

New-Item -ItemType Directory -Force $Salida | Out-Null
$frases = Get-Content -Path $Lineas -Encoding UTF8 | Where-Object { $_.Trim() -ne '' }
for ($i = 0; $i -lt $frases.Count; $i++) {
  $stream = Esperar ($synth.SynthesizeTextToStreamAsync($frases[$i])) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
  $reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
  $n = Esperar ($reader.LoadAsync([uint32]$stream.Size)) ([uint32])
  $bytes = New-Object byte[] $n
  $reader.ReadBytes($bytes)
  [System.IO.File]::WriteAllBytes((Join-Path $Salida ("l$i.wav")), $bytes)
}
Write-Output "$($frases.Count) frases grabadas"
