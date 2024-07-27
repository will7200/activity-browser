#!/usr/bin/env python3
"""
This script is for generating MSI packages
for Windows users.
"""
import os
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from glob import glob

sys.path.append(os.getcwd())

# Elementtree does not support CDATA. So hack it.
WINVER_CHECK = "Installed OR (VersionNT64 &gt; 602)>"


def gen_guid():
    """
    Generate guid
    """
    return str(uuid.uuid4()).upper()


class Node:
    """
    Node to hold path and directory values
    """

    def __init__(self, dirs, files):
        self.check_dirs(dirs)
        self.check_files(files)
        self.dirs = dirs
        self.files = files

    @staticmethod
    def check_dirs(dirs):
        """
        Check to see if directory is instance of list
        """
        assert isinstance(dirs, list)

    @staticmethod
    def check_files(files):
        """
        Check to see if files is instance of list
        """
        assert isinstance(files, list)


class PackageGenerator:
    """
    Package generator for MSI packages
    """

    def __init__(self):
        self.product_name = "Activity Browser"
        self.manufacturer = "The Activity Browser Team"
        self.version = "0.0.2"
        self.root = None
        self.guid = "*"
        self.update_guid = "141527EE-E28A-4D14-97A4-92E6075D28B2"
        self.main_xml = "activitybrowser.wxs"
        self.main_o = "activitybrowser.wixobj"
        self.final_output = "activitybrowser-{}-64.msi".format(self.version)
        self.staging_dirs = ["dist"]
        self.progfile_dir = "ProgramFiles64Folder"
        redist_globs = [
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Redist\\MSVC\\*\\MergeModules\\Microsoft_VC142_CRT_x64.msm",
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Redist\\MSVC\\*\\MergeModules\\Microsoft_VC143_CRT_x64.msm",
        ]
        redist_path = None
        for g in redist_globs:
            trials = glob(g)
            if len(trials) > 1:
                sys.exit("MSM glob matched multiple entries:" + "\n".join(trials))
            if len(trials) == 1:
                redist_path = trials[0]
                break
        if redist_path is None:
            sys.exit("No MSMs found.")
        self.redist_path = redist_path
        self.component_num = 0
        self.feature_properties = {
            self.staging_dirs[0]: {
                "Id": "MainProgram",
                "Title": "Activity Browser",
                "Description": "Activity Browser Executables",
                "Level": "1",
                "AllowAbsent": "no",
            },
        }
        self.feature_components = {}
        for s_d in self.staging_dirs:
            self.feature_components[s_d] = []

    def build_dist(self):
        """
        Build dist file from PyInstaller info
        """
        for sdir in self.staging_dirs:
            if os.path.exists(sdir):
                shutil.rmtree(sdir)
        main_stage = self.staging_dirs[0]

        pyinstaller = shutil.which("pyinstaller")
        if not pyinstaller:
            print("ERROR: This script requires pyinstaller.")
            sys.exit(1)

        pyinstaller_tmpdir = "pyinst-tmp"
        if os.path.exists(pyinstaller_tmpdir):
            shutil.rmtree(pyinstaller_tmpdir)
        pyinst_cmd = [
            pyinstaller,
            "activity-browser.spec",
            # "--clean",
            "--distpath",
            pyinstaller_tmpdir,
        ]
        subprocess.check_call(pyinst_cmd)
        shutil.move(os.path.join(pyinstaller_tmpdir), main_stage)
        self.del_infodirs(main_stage)
        if not os.path.exists(os.path.join(main_stage, "activity-browser.exe")):
            sys.exit("activity-browser exe missing from staging dir.")

    def del_infodirs(self, dirname):
        # Starting with 3.9.something there are some
        # extra metadatadirs that have a hyphen in their
        # file names. This is a forbidden character in WiX
        # filenames so delete them.
        for d in glob(os.path.join(dirname, "*-info")):
            shutil.rmtree(d)

    def generate_files(self):
        """
        Generate package files for MSI installer package
        """
        self.root = ET.Element(
            "Wix",
            {
                "xmlns": "http://wixtoolset.org/schemas/v4/wxs",
                "xmlns:ui": "http://wixtoolset.org/schemas/v4/wxs/ui",
            },
        )
        self.fragments(self.root)

        package = ET.SubElement(
            self.root,
            "Package",
            {
                "Name": self.product_name,
                "UpgradeCode": self.update_guid,
                "Manufacturer": self.manufacturer,
                "Compressed": "yes",
                "Version": self.version,
            },
        )

        ET.SubElement(
            package,
            "SummaryInformation",
            {
                "Keywords": "Installer",
                "Description": "{} {} installer".format(
                    self.product_name, self.version
                ),
                "Manufacturer": self.manufacturer,
                "Comments": "LCA Analysis",
            },
        )

        ET.SubElement(
            package,
            "Launch",
            {
                "Message": "This application is only supported on Windows 10 or higher.",
                "Condition": "X" * len(WINVER_CHECK),
            },
        )

        ET.SubElement(
            package,
            "MajorUpgrade",
            dict(
                DowngradeErrorMessage="A newer version of Activity Browser is already installed.",
                AllowDowngrades="no",
                AllowSameVersionUpgrades="no",
            ),
        )

        ET.SubElement(
            package,
            "Media",
            {
                "Id": "1",
                "Cabinet": "activity-browser.cab",
                "EmbedCab": "yes",
            },
        )
        targetdir = ET.SubElement(
            package,
            "StandardDirectory ",
            {
                "Id": "ProgramFiles64Folder",
            },
        )
        installdir = ET.SubElement(
            targetdir, "Directory", {"Id": "INSTALLDIR", "Name": "Activity Browser"}
        )
        ET.SubElement(
            installdir,
            "Merge",
            {
                "Id": "VCRedist",
                "SourceFile": self.redist_path,
                "DiskId": "1",
                "Language": "0",
            },
        )

        ET.SubElement(
            package,
            "ui:WixUI",
            {
                "Id": "WixUI_FeatureTree",
            },
        )
        for s_d in self.staging_dirs:
            assert os.path.isdir(s_d)
        top_feature = ET.SubElement(
            package,
            "Feature",
            {
                "Id": "Complete",
                "Title": "Activity Browser  " + self.version,
                "Description": "The complete package",
                "Display": "expand",
                "Level": "1",
                "ConfigurableDirectory": "INSTALLDIR",
            },
        )
        ET.SubElement(top_feature, "ComponentRef", dict(Id="ABDesktopShortcut"))
        for s_d in self.staging_dirs:
            nodes = {}
            for root, dirs, files in os.walk(s_d):
                cur_node = Node(dirs, files)
                nodes[root] = cur_node
            self.create_xml(nodes, s_d, installdir, s_d)
            self.build_features(top_feature, s_d)
        vcredist_feature = ET.SubElement(
            top_feature,
            "Feature",
            {
                "Id": "VCRedist",
                "Title": "Visual C++ runtime",
                "AllowAdvertise": "no",
                "Display": "hidden",
                "Level": "1",
            },
        )
        ET.SubElement(vcredist_feature, "MergeRef", {"Id": "VCRedist"})
        directory_ref = ET.SubElement(
            package, "StandardDirectory", dict(Id="DesktopFolder")
        )
        desktop_short_cut = ET.SubElement(
            directory_ref,
            "Component",
            {"Id": "ABDesktopShortcut", "Guid": "*"},
        )
        shortcut = ET.SubElement(
            desktop_short_cut,
            "Shortcut",
            dict(
                Id="abDesktopShortCut",
                Name="Activity Browser",
                Description="Activity Browser",
                Directory="DesktopFolder",
                Target="[INSTALLDIR]activity-browser.exe",
                WorkingDirectory="INSTALLDIR",
                Icon="ABIcon",
            ),
        )
        shortcut2 = ET.SubElement(
            desktop_short_cut,
            "Shortcut",
            dict(
                Id="abProgramMenuShortCut",
                Name="Activity Browser",
                Description="Activity Browser",
                Directory="ProgramMenuFolder",
                Target="[INSTALLDIR]activity-browser.exe",
                WorkingDirectory="INSTALLDIR",
                Icon="ABIcon",
            ),
        )
        ET.SubElement(
            desktop_short_cut,
            "RemoveFolder",
            dict(Id="cmdDesktopShortCut", On="uninstall"),
        )
        ET.SubElement(
            desktop_short_cut,
            "RegistryValue",
            dict(
                Root="HKCU",
                Name="installed",
                Type="integer",
                Value="1",
                KeyPath="yes",
                Key=r"Software\LCA-Activity Browser\Activity Browser",
            ),
        )
        ET.ElementTree(self.root).write(
            self.main_xml, encoding="utf-8", xml_declaration=True
        )
        # ElementTree can not do prettyprinting so do it manually
        import xml.dom.minidom

        doc = xml.dom.minidom.parse(self.main_xml)
        with open(self.main_xml, "w") as open_file:
            open_file.write(doc.toprettyxml())

        # One last fix, add CDATA.
        with open(self.main_xml) as open_file:
            data = open_file.read()
        data = data.replace("X" * len(WINVER_CHECK), WINVER_CHECK)
        with open(self.main_xml, "w") as open_file:
            open_file.write(data)

    def fragments(self, root):
        fragment = ET.SubElement(root, "Fragment")
        ET.SubElement(
            fragment,
            "Icon",
            {
                "Id": "ABIcon",
                "SourceFile": os.path.abspath(
                    r"activity_browser\static\icons\activity-browser.ico"
                ),
            },
        )

    def build_features(self, top_feature, staging_dir):
        """
        Generate build features
        """
        feature = ET.SubElement(
            top_feature, "Feature", self.feature_properties[staging_dir]
        )
        for component_id in self.feature_components[staging_dir]:
            ET.SubElement(
                feature,
                "ComponentRef",
                {
                    "Id": component_id,
                },
            )

    def create_xml(self, nodes, current_dir, parent_xml_node, staging_dir):
        """
        Create XML file
        """
        cur_node = nodes[current_dir]
        if cur_node.files:
            component_id = "ApplicationFiles{}".format(self.component_num)
            comp_xml_node = ET.SubElement(
                parent_xml_node,
                "Component",
                {
                    "Id": component_id,
                    "Bitness": "always64",
                    "Guid": gen_guid(),
                },
            )
            self.feature_components[staging_dir].append(component_id)
            if self.component_num == 0:
                ET.SubElement(
                    comp_xml_node,
                    "Environment",
                    {
                        "Id": "Environment",
                        "Name": "PATH",
                        "Part": "last",
                        "System": "yes",
                        "Action": "set",
                        "Value": "[INSTALLDIR]",
                    },
                )
            self.component_num += 1
            for f_node in cur_node.files:
                file_id = (
                    os.path.join(current_dir, f_node)
                    .replace("\\", "_")
                    .replace("#", "_")
                    .replace("-", "_")
                    .replace("+", "_")[:72]
                )
                ET.SubElement(
                    comp_xml_node,
                    "File",
                    {
                        "Id": file_id,
                        "Name": f_node,
                        "Source": os.path.join(current_dir, f_node),
                    },
                )

        for dirname in cur_node.dirs:
            dir_id = (
                os.path.join(current_dir, dirname)
                .replace("\\", "_")
                .replace("/", "_")
                .replace("-", "_")
            )
            dir_node = ET.SubElement(
                parent_xml_node,
                "Directory",
                {
                    "Id": dir_id,
                    "Name": dirname,
                },
            )
            self.create_xml(
                nodes, os.path.join(current_dir, dirname), dir_node, staging_dir
            )

    def build_package(self):
        """
        Generate the MSI package.
        """
        subprocess.check_call(
            [
                "wix",
                "build",
                '-bindvariable', 'WixUILicenseRtf=LICENSE.rtf',
                "-ext",
                "WixToolset.UI.wixext",
                "-culture",
                "en-us",
                "-arch",
                "x64",
                "-o",
                self.final_output,
                self.main_xml,
            ]
        )


def install_wix():
    subprocess.check_call(
        ["dotnet", "nuget", "add", "source", "https://api.nuget.org/v3/index.json"]
    )
    subprocess.check_call(["dotnet", "tool", "install", "--global", "wix"])
    subprocess.check_call(
        [
            "wix",
            "extension",
            "add",
            "WixToolset.UI.wixext",
        ]
    )


if __name__ == "__main__":
    if not os.path.exists("activity-browser.spec"):
        sys.exit(print("Run me in the top level source dir."))
    if not shutil.which("wix"):
        install_wix()
    # subprocess.check_call(["pip", "install", "--upgrade", "pyinstaller"])

    p = PackageGenerator()
    p.build_dist()
    p.generate_files()
    p.build_package()
