param([ValidateRange(1,1000)][int]$PageSize = 50, [string]$OutputDirectory = 'data')
$ErrorActionPreference = 'Stop'
$base = 'https://apiv2.business.gov.vn'
$out = Join-Path $PSScriptRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $out | Out-Null
function Read-PublicPage([string]$Url) {
    for ($attempt=1; $attempt -le 4; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri $Url -TimeoutSec 45 -Headers @{Accept='application/json'}
            if ($response.success -eq $false) { throw 'API returned success=false' }
            return $response.result
        } catch {
            if ($attempt -eq 4) { throw }
            Start-Sleep -Seconds ([Math]::Pow(2,$attempt))
        }
    }
}
function Read-Listing([string]$Name,[string]$Endpoint,[string]$Filter) {
    $all = [Collections.Generic.List[object]]::new()
    $seen = [Collections.Generic.HashSet[string]]::new()
    $skip=0
    do {
        $url = "$base/api/services/app/$Endpoint`?MaxResultCount=$PageSize&SkipCount=$skip&Sorting=LastModificationTime%20DESC$Filter"
        $page = Read-PublicPage $url
        if ($null -eq $page.totalCount -or $null -eq $page.items) { throw "Invalid listing: $Name" }
        $new=0
        foreach ($item in $page.items) {
            if ($seen.Add([string]$item.id)) { $all.Add($item); $new++ }
        }
        $skip += @($page.items).Count
        Write-Host "$Name : $skip / $($page.totalCount)"
        if ($new -eq 0 -and $skip -lt $page.totalCount) { throw "Pagination stopped making progress: $Name" }
        Start-Sleep -Milliseconds 400
    } while ($skip -lt $page.totalCount)
    if ($all.Count -ne $page.totalCount) { throw "Count mismatch: $Name $($all.Count) / $($page.totalCount)" }
    # Keep business fields only; exclude personal identity and internal audit fields.
    if ($Name -ne 'products') {
        $fields = @('id','tenGiaoDich','tenTiengAnh','tenVietTat','maSoThue','ngayThanhLap','loaiHinhDoanhNghiep','diaChi','email','dienThoai','website','websites','vonDieuLe','tongSoLaoDong','nguoiDaiDien','chucVuNguoiDaiDien','emailNguoiDaiDien','dienThoaiNguoiDaiDien','tenTinhThanh','tenQuanHuyen','tenQuocGia','tenVungKinhTe','maTinhThanh','maQuanHuyen','quocGiaTruSoChinh','vungKinhTe','nganhNgheChinh','nganhNgheChinhId','nganhNghes','hiepHoiIds','tenHiepHois','doanhThuBinhQuan3Nam','laoDongBinhQuan3Nam','tongVonBinhQuan3Nam','lastModificationTime','fileVaults','moTa')
        $all = @($all | Select-Object -Property $fields)
    }
    ConvertTo-Json -InputObject @($all) -Depth 25 | Set-Content -LiteralPath (Join-Path $out "$Name.json") -Encoding utf8
    return [pscustomobject]@{source=$Name;count=@($all).Count;expected=$page.totalCount;endpoint=$Endpoint}
}
$runs = @()
$runs += Read-Listing 'companies_v1' 'DoanhNghiep/GetListDoanhNghiep' '&Loai=0&Loai=1&Loai=2&IsActive=true'
$runs += Read-Listing 'companies_b2b' 'DoanhNghiep/GetListDoanhNghiepB2b' '&Loai=0&Loai=1&Loai=2&IsActive=true'
$runs += Read-Listing 'products' 'ProductCorporation/GetAll' ''
[pscustomobject]@{scraped_at=[DateTimeOffset]::Now.ToString('o');sources=$runs} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'run.json') -Encoding utf8
Write-Host 'Completed all listings.'
