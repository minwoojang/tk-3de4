import sys
import os
import subprocess
import tempfile

import sgtk
from sgtk.platform import SoftwareLauncher, LaunchInformation, SoftwareVersion

class TDE4Launcher(SoftwareLauncher):
    """
    Handles launching 3DEqualizer4 executables. Automatically starts up
    a tk-3de4 engine with the current context in the new session
    of 3DEqualizer4.
    """
    test = "O:\\inhouse\\3de"
    def prepare_launch(self, exec_path, args, file_to_open=None):
        """
        Prepares an environment to launch 3DEqualizer4 in that will automatically
        load Toolkit and the tk-3de4 engine when 3DEqualizer starts.

        :param str exec_path: Path to 3DEqualizer4 executable to launch.
        :param str args: Command line arguments as strings.
        :param str file_to_open: (optional) Full path name of a file to open on launch.
        :returns: :class:`LaunchInformation` instance
        """
        required_env = {}

        # Run the engine's startup/*.py files when 3DEqualizer starts up
        startup_path = os.path.join(self.disk_location, 'startup')

        # Get path to temp menu folder, and add it to the environment.
        menufolder = tempfile.mkdtemp(prefix='tk-3dequalizer_')
        required_env['TK_3DE4_MENU_DIR'] = menufolder

        required_env['PYTHON_CUSTOM_SCRIPTS_3DE4'] = os.pathsep.join(
            [x for x in os.getenv('PYTHON_CUSTOM_SCRIPTS_3DE4', '').split(os.pathsep) if x]
            + [startup_path, menufolder,self.test])

        # Add context information info to the env.
        required_env["TANK_CONTEXT"] = sgtk.Context.serialize(self.context)

        # open a file
        if file_to_open:
            args += " {}".format(subprocess.list2cmdline(("-open", file_to_open)))

        return LaunchInformation(exec_path, args, required_env)
   

    def scan_software(self):
        """
        Scan the filesystem for natron executables.

        :return: A list of :class:`SoftwareVersion` objects.
        """

        try:
            import rez as _

        except ImportError:
            rez_path = self.get_rez_module_root()
            if not isinstance(rez_path, str):
                rez_path = rez_path.decode('utf-8')
            if not rez_path:
                raise EnvironmentError('rez is not installed and could not be automatically found. Cannot continue.')

            sys.path.append(rez_path)

        from rez.package_search import ResourceSearcher, ResourceSearchResultFormatter


        searcher = ResourceSearcher()
        formatter = ResourceSearchResultFormatter()
        _ ,packages = searcher.search("3de")

        supported_sw_versions = []
        self.logger.debug("Scanning for 3de executables...")
        infos = formatter.format_search_results(packages)
        
        for info in infos:
            name,version = info[0].split("-")

            software = SoftwareVersion(version,name,"3de",self._icon_from_engine())
            supported_sw_versions.append(software)

        return supported_sw_versions


    def _icon_from_engine(self):
        """
        Use the default engine icon as natron does not supply
        an icon in their software directory structure.

        :returns: Full path to application icon as a string or None.
        """

        # the engine icon
        engine_icon = os.path.join(self.disk_location, "icon_256.png")

        return engine_icon


    def get_rez_module_root(self):
        
        
        command = self.get_rez_root_command()
        module_path, stderr = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

        module_path = module_path.strip()

        if not stderr and module_path:
            return module_path

        return ''


    def get_rez_root_command(self):

        return 'rez-env rez -- echo %REZ_REZ_ROOT%'