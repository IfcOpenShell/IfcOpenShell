param(
  $URL,
  $File
)


#$URL = "http://download.microsoft.com/download/E/7/6/E76850B8-DA6E-4FF5-8CCE-A24FC513FD16/Windows6.0-KB2506146-x64.msu"
#$URL="http://downloads.sourceforge.net/project/boost/boost/1.59.0/boost_1_59_0.7z"
#$URL="https://github.com/e-task/IfcOpenShell/blob/master/README.md"
#$File="download.test"

# Sample
# powershell -File DownloadFile.ps1 "http://downloads.sourceforge.net/project/boost/boost/1.59.0/boost_1_59_0.7z" "boost_1_59_0.7z"
# powershell -File DownloadFile.ps1 "https://github.com/e-task/IfcOpenShell/blob/master/README.md" "download.test"

Write-Host Download $URL
Write-Host => $File

    $uri = New-Object "System.Uri" "$URL"
    $request = [System.Net.HttpWebRequest]::Create($uri)
    $request.set_Timeout(150000) #150 second timeout
    $response = $request.GetResponse()
    $totalLength = [System.Math]::Floor($response.get_ContentLength()/1024)
    $responseStream = $response.GetResponseStream()
    $targetStream = New-Object -TypeName System.IO.FileStream -ArgumentList $File, Create
    $buffer = new-object byte[] 10KB
    $count = $responseStream.Read($buffer,0,$buffer.length)
    $downloadedBytes = $count
    while ($count -gt 0)
    {
        [System.Console]::CursorLeft = 0
        [System.Console]::Write("Downloaded {0}K of {1}K", [System.Math]::Floor($downloadedBytes/1024), $totalLength)
        $targetStream.Write($buffer, 0, $count)
        $count = $responseStream.Read($buffer,0,$buffer.length)
        $downloadedBytes = $downloadedBytes + $count
    }
    "`nFinished Download"
    $targetStream.Flush()
    $targetStream.Close()
    $targetStream.Dispose()
    $responseStream.Dispose() 