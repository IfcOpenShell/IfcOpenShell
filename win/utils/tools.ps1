Set-PSDebug -Trace 0
Set-StrictMode -Version 3
$ErrorActionPreference = "Stop"

$cecho = "$PSScriptRoot\cecho.cmd"


# Create marker file to indicate whether Release or Debug build was installed.
function mark {
    param(
        [Parameter(Mandatory = $true)]
        [string]$installation_dir
    )

    if (-not (Test-Path -Path $installation_dir)) {
        throw "Directory '$installation_dir' does not exist."
    }

    $marker_filepath = Join-Path -Path $installation_dir -ChildPath $ENV:MARKER_FILE
    if (Test-Path -Path $marker_filepath) {
        return
    }
    . $cecho 0 13 "Marking installation in '$installation_dir' with '$ENV:MARKER_FILE'."
    New-Item -Path $marker_filepath -ItemType File | Out-Null
}

# This function can be deprecated in the future, since installations are marked automatically.
# It's here only to avoid some disruption during the transition period.
function mark_based_on_artifacts {
    param(
        [Parameter(Mandatory = $true)]
        [string]$dependency_name,

        [Parameter(Mandatory = $true)]
        [string]$installation_dir
    )

    if ($dependency_name -eq "hdf5") {
        if ($env:BUILD_CFG -eq "Debug") {
            $artifact = "lib\libhdf5_D.lib"
        }
        else {
            $artifact = "lib\libhdf5.lib"
        }
    }
    elseif ($dependency_name -eq "opencollada") {
        if ($env:BUILD_CFG -eq "Debug") {
            $artifact = "lib\opencollada\OpenCOLLADAFrameworkd.lib"
        }
        else {
            $artifact = "lib\opencollada\OpenCOLLADAFramework.lib"
        }
    }
    elseif ($dependency_name -eq "OpenCASCADE") {
        # New OCCT folder layout was introduced after marker files were added,
        # so installation don't need artifact-based detection.
        return
    }
    elseif ($dependency_name -eq "rocksdb") {
        if ($env:BUILD_CFG -eq "Debug") {
            $artifact = "lib\rocksdb_d.lib"
        }
        else {
            $artifact = "lib\rocksdb.lib"
        }
    }
    else {
        throw "Unexpected dependency name '$dependency_name'."
    }
    $artifact_filepath = Join-Path -Path $installation_dir -ChildPath $artifact
    if (-not (Test-Path -Path $artifact_filepath)) {
        return
    }
    if (-not (Test-Path -Path $installation_dir)) {
        throw "Directory '$installation_dir' does not exist."
    }
    $marker_filepath = Join-Path -Path $installation_dir -ChildPath $ENV:MARKER_FILE
    if (Test-Path -Path $marker_filepath) {
        return
    }
    . $cecho 0 13 "Found artifact '$artifact' for dependency '$dependency_name' $env:BUILD_CFG."
    & mark $installation_dir
}

# Check if installation exists for the current `BUILD_CFG`.
# Returns exit code 200 if installation exists, 404 otherwise.
# Since we want Release and Debug installation to coexist,
# we add special marker file to indicate which build type was installed.
function check_installation {
    param(
        [Parameter(Mandatory = $true)]
        [string]$dependency_name,
        [Parameter(Mandatory = $true)]
        [string]$installation_dir
    )

    if (-not (Test-Path -Path $installation_dir)) {
        exit 404
    }

    & mark_based_on_artifacts $dependency_name $installation_dir

    $marker_filepath = Join-Path -Path $installation_dir -ChildPath $ENV:MARKER_FILE
    if (-not (Test-Path -Path $marker_filepath)) {
        exit 404
    }
    exit 200
}


# Dependencies Release/Debug configs compatibility:
# - hdf5: incompatible
# - OpenCASCADE: incompatible
# - rocksdb: incompatible
# - opencollada: incompatible
# - zstd: compatible

function setup_build_cfg {
    if (-not $env:BUILD_CFG) {
        throw "Variable 'BUILD_CFG' is not defined."
    }
    if ($env:BUILD_CFG -eq "Debug") {
        $ENV:MARKER_FILE = ".debug_installation"
    }
    else {
        $ENV:MARKER_FILE = ".release_installation"
    }
}


function extract_file {
    param(
        [Parameter(Mandatory = $true)]
        [string]$dependency_name,
        [Parameter(Mandatory = $true)]
        [string]$filename,
        [Parameter(Mandatory = $true)]
        [string]$destination_dir,
        [Parameter(Mandatory = $true)]
        [string]$dir_after_extraction
    )
    if (Test-Path -Path "$dir_after_extraction") {
        . $cecho 0 13 "$dependency_name already extracted into '$dir_after_extraction'. Skipping."
        return
    }
    . $cecho 0 13 "Extracting $dependency_name into '$destination_dir' from '$filename'."
    7za x "$filename" -o"$destination_dir"
}


function download_file {
    param(
        [Parameter(Mandatory = $true)]
        [string]$dependency_name,
        [Parameter(Mandatory = $true)]
        [string]$url,
        [Parameter(Mandatory = $true)]
        [string]$destination_dir,
        [Parameter(Mandatory = $true)]
        [string]$filename
    )
    mkdir "$destination_dir" -Force | Out-Null
    pushd "$destination_dir"
    if (Test-Path -Path "$filename") {
        . $cecho 0 13 "$dependency_name already downloaded. Skipping."
        return
    }

    . $cecho 0 13 "Downloading $dependency_name into '$destination_dir'"
    Invoke-WebRequest $url -OutFile $filename
}


# Required env variables:
# - DEPS_DIR
function git_clone_and_checkout_revision {
    param(
        [Parameter(Mandatory = $true)]
        [string]$dependency_name,
        [Parameter(Mandatory = $true)]
        [string]$git_url,
        [Parameter(Mandatory = $true)]
        [string]$dest_dir,
        [Parameter(Mandatory = $false)]
        [string]$revision
    )
    if (Test-Path -Path "$dest_dir") {
        . $cecho 0 13 "Cloning $dependency_name is already cloned."
        return
    }
    . $cecho 0 13 "Cloning $dependency_name into '$dest_dir'."
    pushd "$env:DEPS_DIR"
    git clone $git_url $dest_dir
    popd

    pushd "$dest_dir"
    git fetch
    . $cecho 0 13 "Checking out $dependency_name revision $revision."
    git reset --hard
    git checkout $revision
    popd
}

function install_cmake_project {
    param(
        [Parameter(Mandatory = $true)]
        [string]$dependency_name,
        [Parameter(Mandatory = $true)]
        [string]$build_dir,
        [Parameter(Mandatory = $true)]
        [string]$configuration
    )
    pushd "$build_dir"
    . $cecho 0 13 "Installing $dependency_name ($configuration). Please be patient, this may take a while."
    $command = "cmake --install . --config $configuration"
    . $cecho 0 13 "$command"
    Invoke-Expression $command
    popd
}


function check_boost_vc145_compatibility {
    param(
        [Parameter(Mandatory = $true)]
        [string]$VC_VER,
        [Parameter(Mandatory = $true)]
        [string]$DEPS_DIR,
        [Parameter(Mandatory = $true)]
        [string]$BOOST_ROOT
    )

    $boost_build_path = "$BOOST_ROOT/tools/build"

    if ($VC_VER -ne "14.5") {
        . $cecho 0 13 "VC_VER is not 14.5, no need to install updated b2."
        return
    }

    $res = Select-String -Path "$boost_build_path/src/engine/build.bat" -Pattern 'vc143, vc145' -Quiet;
    if ($res) {
        . $cecho 0 13 "vc145 already supported, no need to install updated b2."
        return
    }

    $b2_version = "5.4.2"
    $b2_stem = "b2-$b2_version"
    $b2_path = "$DEPS_DIR\$b2_stem"
    $b2_filename = "$b2_stem.zip"

    & download_file "b2" "https://github.com/bfgroup/b2/releases/download/$b2_version/$b2_filename" "$DEPS_DIR" "$b2_filename"
    & extract_file "b2" "$b2_filename" "$DEPS_DIR" "$b2_path"

    . $cecho 0 13 "Installing b2 with vc145 support..."
    Remove-Item -Recurse -Path "$boost_build_path"
    Copy-Item -Path "$b2_path" -Destination "$boost_build_path" -Recurse
    . $cecho 0 13 "b2 with vc145 support installed."
}

function main {
    & setup_build_cfg
    # Dispatch command.
    $command = $Args[0]
    if ($args.Count -gt 1) {
        $command_args = $Args[1..($args.Count - 1)]
    }
    else {
        $command_args = @()
    }
    & $command @command_args
}

& main @Args
exit 0
