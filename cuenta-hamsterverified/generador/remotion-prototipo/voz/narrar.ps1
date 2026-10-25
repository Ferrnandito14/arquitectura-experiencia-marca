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
$synth.Voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.DisplayName -eq 'Microsoft Pablo' }
$synth.Options.SpeakingRate = 1.05

$lineas = @(
  '¿Por qué nadie responde tus correos?',
  'Te lo explico en una línea.',
  'Un correo, una pregunta. Y di para cuándo la necesitas.',
  'Si mandas tres preguntas, te van a contestar una.',
  'Palabra de hámster.'
)
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
for ($i = 0; $i -lt $lineas.Count; $i++) {
  $stream = Esperar ($synth.SynthesizeTextToStreamAsync($lineas[$i])) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
  $reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
  $n = Esperar ($reader.LoadAsync([uint32]$stream.Size)) ([uint32])
  $bytes = New-Object byte[] $n
  $reader.ReadBytes($bytes)
  [System.IO.File]::WriteAllBytes((Join-Path $dir ("l$i.wav")), $bytes)
  "l$i.wav $n bytes"
}
