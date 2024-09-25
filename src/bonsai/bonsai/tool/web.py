# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from ifcopenshell.util.classification import get_classification_data, get_references
from ifcopenshell.util.selector import filter_elements
import ifcopenshell.util.cost
import bpy
from bonsai.bim.module.web.data import WebData
from ifcopenshell.util.element import get_psets, get_type, has_property
import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.api.sequence
import ifcopenshell.api.cost
from typing import Any, Dict, Optional
import time
import socket
import sys
import os
import errno
import subprocess
import webbrowser
import asyncio
import socketio
import threading
import queue
import json
from time import sleep
from pathlib import Path
import bonsai.core.sequence
import bonsai.core.cost
from ifc5d.ifc2json import ifc5D2json
from bonsai.bim.ifc import IfcStore

sio = None
ws_process = None
ws_thread = None
web_operator_queue = queue.Queue()

RECONNECTION_ATTEMPTS = 3
RECONNECTION_DELAY = 2
IFC_TASK_ATTRIBUTE_MAP = {
    "pStart": "ScheduleStart",
    "pEnd": "ScheduleFinish",
    "pName": "Name",
}


class Web(bonsai.core.tool.Web):
    @classmethod
    def generate_port_number(cls) -> int:
        """
        Generate a free port number.

        This method creates a temporary socket to bind to a free port.
        It then retrieves the port number, and returns it.

        Returns:
            int: The port number that was generated.
        """
        print("Generating port number")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))  # Bind to a free port
            port = s.getsockname()[1]  # get the bound port
            print(f"Port number: {port}")
            return port

    @classmethod
    def is_port_available(cls, port: int) -> bool:
        """
        Attempts to connect to the specified port on localhost.

        If the connection is refused, the port is available for use; otherwise, it is in use.

        Args:
           port (int): The port number to check.

        Returns:
            bool: True if the port is available, False if it is in use.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # connect_ex returns errno.SUCCESS (0) if the connection succeeds
            # otherwise returns errno.ECONNREFUSED (111 or 10061) if no server is listening
            return s.connect_ex(("localhost", port)) == errno.ECONNREFUSED

    @classmethod
    def start_websocket_server(cls, port: int) -> None:
        """
        Starts a WebSocket server on the specified port.

        This method sets up the environment, locates paths, and starts
        the WebSocket server process.

        Args:
           port (int): The port number on which to start the WebSocket server.
        """
        import addon_utils

        global ws_process

        webui_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui")
        ws_path = os.path.join(webui_path, "sioserver.py")

        py_version = sys.version_info

        if bpy.app.version >= (4, 2, 0):
            bonsai_lib_path = (
                Path(bpy.utils.user_resource("EXTENSIONS"))
                / ".local"
                / "lib"
                / f"python{py_version.major}.{py_version.minor}"
                / "site-packages"
            )
        else:
            addon = [a for a in addon_utils.modules() if a.bl_info["name"] == "Bonsai"][0]
            bonsai_path = os.path.dirname(addon.__file__)
            bonsai_lib_path = os.path.join(bonsai_path, "libs", "site", "packages")

        env = os.environ.copy()
        env["BONSAI_LIB_PATH"] = str(bonsai_lib_path)
        env["BONSAI_VERSION"] = tool.Blender.get_bonsai_version()

        ws_process = subprocess.Popen(
            [sys.executable, ws_path, "--p", str(port), "--host", "127.0.0.1"],
            cwd=webui_path,
            env=env,
        )

        cls.set_is_running(True)

    @classmethod
    def connect_websocket_server(cls, port: int) -> None:
        """
        Connect to a WebSocket server on the specified port.

        This method sets up an asynchronous Socket.IO client with
        reconnection attempts, starts an asyncio thread, connects to the WebSocket server, and sets the connection status.

        Args:
           port (int): The port number to connect to the WebSocket server.
        """
        global ws_thread, sio

        if bpy.context.scene.WebProperties.is_connected:
            print(f"Already connected to websocket server on port: {port}")
            return

        sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=RECONNECTION_ATTEMPTS,
            reconnection_delay=RECONNECTION_DELAY,
            logger=True,
        )

        ws_thread = AsyncioThread()
        ws_thread.daemon = True
        ws_thread.start()

        ws_url = f"ws://localhost:{port}/blender"
        ws_thread.run_coro(cls.sio_connect(ws_url))
        cls.set_is_connected(True)
        bpy.app.timers.register(cls.check_operator_queue)

    @classmethod
    def disconnect_websocket_server(cls) -> None:
        """
        Disconnects the WebSocket server and stops the associated thread.

        This method is responsible for disconnecting the WebSocket server, stopping the asyncio thread,
        and resetting the global variables related to the WebSocket connection.
        """
        global ws_thread, sio
        ws_thread.run_coro(cls.sio_disconnect())
        ws_thread.stop()
        ws_thread = None
        sio = None
        cls.set_is_connected(False)

    @classmethod
    def kill_websocket_server(cls) -> None:
        """
        Terminate the currently running WebSocket server.

        This method checks if there is an active WebSocket server process. If so, it disconnects it (if connected),
        removes its PID from the PID file, terminates the process, and updates the server's running status.
        """
        global ws_process

        if ws_process is None:
            print("No Websocket server running")
            return

        if bpy.context.scene.WebProperties.is_connected:
            cls.disconnect_websocket_server()

        # sleep(0.5)
        webui_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui")
        pid_file = os.path.join(webui_path, "running_pid.json")
        with open(pid_file, "r") as f:
            pids = json.load(f)

        if str(ws_process.pid) in pids:
            del pids[str(ws_process.pid)]

        # Write the updated PIDs back to the file
        with open(pid_file, "w") as f:
            json.dump(pids, f, indent=4)

        ws_process.kill()
        ws_process = None

        cls.set_is_running(False)
        print("Websocket server killed successfully")

    @classmethod
    def has_started(cls, port: int) -> bool:
        """
        Check if the WebSocket server has started on the specified port.

        this method continuously checks for the existence of the WebSocket server's process ID (PID) in the running_pid JSON file.
        It waits for a maximum of 5 seconds before returning False.

        Args:
            port (int): The port number on which the WebSocket server is expected to be running.

        Returns:
            bool: True if the WebSocket server has started on the specified port within the maximum time limit, False otherwise.
        """
        pid = ws_process.pid
        max_time = 5
        start = time.time()
        while True:
            if time.time() - start > max_time:
                return False
            webui_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "webui")
            pid_file = os.path.join(webui_path, "running_pid.json")
            try:
                with open(pid_file, "r") as f:
                    data = json.load(f)
                    if data.get(str(pid)) == port:
                        return True
            except:
                pass
            time.sleep(0.1)

    @classmethod
    def send_webui_data(
        cls,
        data: Optional[Any] = None,
        data_key: str = "data",
        event: str = "data",
        namespace: str = "/blender",
        use_web_data: bool = True,
    ) -> None:
        """
        Sends data to the Web UI via Websocket connection.

        Args:
            data (Optional[Any]): The data to send. If None, just sends data from WebData.
            data_key (str): The key under which to store the data in the payload. Defaults to "data".
            event (str): The WebSocket event to emit. Defaults to "data".
            namespace (str): The namespace for the WebSocket event. Defaults to "/blender".
            use_web_data (bool): Whether to use data from WebData. Defaults to True.
        """

        global ws_thread
        payload = {}

        if use_web_data:
            if not WebData.is_loaded:
                WebData.load()
            payload = WebData.data.copy()

        if data is not None:
            payload[data_key] = data

        if ws_thread is not None and bpy.context.scene.WebProperties.is_connected:
            ws_thread.run_coro(cls.sio_send(payload, event, namespace))

    @classmethod
    def check_operator_queue(cls) -> None | float:
        """
        this method checks the operator queue and processes the operators based on the source page.
        If the WebProperties.is_connected is False, it clears the queue and returns None to unregister the timer.
        If the queue is not empty, it processes each operator by calling the corresponding handling function.

        Returns:
            (Optional[float]): Returns None if the WebProperties.is_connected is False, otherwise returns 1.0 to continue the timer.
        """
        if not bpy.context.scene.WebProperties.is_connected:
            with web_operator_queue.mutex:
                web_operator_queue.queue.clear()
            return None  # unregister timer if not connected

        while not web_operator_queue.empty():
            operator = web_operator_queue.get_nowait()
            if not operator:
                continue
            if operator["sourcePage"] == "csv":
                cls.handle_csv_operator(operator["operator"])
            elif operator["sourcePage"] == "gantt":
                cls.handle_gantt_operator(operator["operator"])
            elif operator["sourcePage"] == "drawings":
                cls.handle_drawings_operator(operator["operator"])
            elif operator["sourcePage"] == "demo":
                message = operator["operator"]["message"]
                print(f"Message from demo page: {message}")
            elif operator["sourcePage"] == "cost":
                cls.handle_cost_operator(operator["operator"])
        return 1.0

    @classmethod
    def handle_csv_operator(cls, operator_data: dict) -> None:
        """
        this method handles the Schedules page operators.

        Args:
            operator_data (dict): A dictionary containing the operator data.
        """
        if operator_data["type"] == "selection":
            bpy.ops.object.select_all(action="DESELECT")
            guid = operator_data["globalId"]
            ele = tool.Ifc.get().by_guid(guid)
            obj = tool.Ifc.get_object(ele)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

    @classmethod
    def handle_cost_operator(cls, operator_data: dict) -> None:
        """
        this method handles the Cost page operators.

        Args:
            operator_data (dict): A dictionary containing the operator data.
        """

        ifc_file = tool.Ifc.get()
        if operator_data["type"] == "getPredefinedTypes":
            cls.send_webui_data(
                data=ifcopenshell.util.cost.get_cost_schedule_types(ifc_file),
                data_key="predefined_types",
                event="predefined_types",
            )
        if operator_data["type"] == "addCostSchedule":
            bonsai.core.cost.add_cost_schedule(
                tool.Ifc, name=operator_data["name"], predefined_type=operator_data["predefinedType"]
            )
            cost_schedules_json = [cs.get_info(recursive=True) for cs in ifc_file.by_type("IfcCostSchedule")]
            currency = tool.Cost.currency()
            cls.send_webui_data(
                data={"cost_schedules": cost_schedules_json, "currency": currency},
                data_key="cost_schedules",
                event="cost_schedules",
            )
        if operator_data["type"] == "getCostSchedules":
            cost_schedules_json = [cs.get_info(recursive=True) for cs in ifc_file.by_type("IfcCostSchedule")]
            currency = tool.Cost.currency()
            cls.send_webui_data(
                data={"cost_schedules": cost_schedules_json, "currency": currency},
                data_key="cost_schedules",
                event="cost_schedules",
            )
        if operator_data["type"] == "loadCostSchedule":
            cost_schedule = ifc_file.by_id(operator_data["costScheduleId"])
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "selectAssignedElements":
            cost_item = tool.Ifc.get().by_id(operator_data["costItemId"])
            products = tool.Cost.get_cost_item_products(cost_item, is_deep=True)
            tool.Spatial.select_products(products, unhide=True)
        if operator_data["type"] == "addSummaryCostItem":
            cost_schedule = ifc_file.by_id(operator_data["costScheduleId"])
            tool.Ifc.run("cost.add_cost_item", cost_schedule=cost_schedule)
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "addCostItem":
            if not operator_data["costItemId"]:
                return
            cost_item = tool.Ifc.get().by_id(operator_data["costItemId"])
            tool.Ifc.run("cost.add_cost_item", cost_item=cost_item)
            cost_schedule = tool.Cost.get_cost_schedule(cost_item=cost_item)
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "deleteCostItem":
            cost_item = tool.Ifc.get().by_id(operator_data["costItemId"])
            cost_schedule = tool.Cost.get_cost_schedule(cost_item=cost_item)
            tool.Ifc.run("cost.remove_cost_item", cost_item=cost_item)
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "duplicateCostItem":
            cost_item = tool.Ifc.get().by_id(operator_data["costItemId"])
            cost_schedule = tool.Cost.get_cost_schedule(cost_item=cost_item)
            tool.Ifc.run("cost.copy_cost_item", cost_item=cost_item)
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "editCostItemName":
            cost_item = tool.Ifc.get().by_id(operator_data["costItemId"])
            tool.Ifc.run("cost.edit_cost_item", cost_item=cost_item, attributes={"Name": operator_data["name"]})
        if operator_data["type"] == "enableEditingCostValues":
            cost_item = tool.Ifc.get().by_id(operator_data["costItemId"])
            cost_values = ifcopenshell.util.cost.get_cost_values(cost_item)
            cls.send_webui_data(
                data={"cost_values": cost_values, "cost_item_id": operator_data["costItemId"]},
                data_key="cost_values",
                event="cost_values",
            )
        if operator_data["type"] == "addCostValue":
            value = ifcopenshell.api.cost.add_cost_value(
                ifc_file,
                parent=ifc_file.by_id(operator_data["costItemId"]),
            )
            cls.send_webui_data(
                data={"cost_value_id": value.id(), "cost_item_id": operator_data["costItemId"]},
                data_key="cost_value",
                event="cost_value",
            )
        if operator_data["type"] == "addSumCostValue":
            cost_item = ifc_file.by_id(operator_data["costItemId"])
            value = tool.Ifc.run("cost.add_cost_value", parent=cost_item)
            tool.Ifc.run("cost.edit_cost_value", cost_value=value, attributes={"Category": "*"})
            cost_schedule = tool.Cost.get_cost_schedule(cost_item=cost_item)
            cls.load_cost_schedule_web_ui(cost_schedule)

        if operator_data["type"] == "deleteCostValue":
            cost_item = ifc_file.by_id(operator_data["costItemId"])
            cost_value = ifc_file.by_id(operator_data["costValueId"])
            tool.Ifc.run("cost.remove_cost_value", parent=cost_item, cost_value=cost_value)
            cost_schedule = tool.Cost.get_cost_schedule(cost_item=cost_item)
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "editCostValues":
            cost_item_id = operator_data["costItemId"]
            cost_item = ifc_file.by_id(cost_item_id)
            cost_schedule = tool.Cost.get_cost_schedule(cost_item=cost_item)
            for value_data in operator_data["costValues"] or []:
                value = ifc_file.by_id(value_data["id"])
                attributes = {}
                if value_data["costType"] == "FIXED":
                    attributes = {"AppliedValue": value_data["appliedValue"], "Category": None}
                elif value_data["costType"] == "CATEGORY":
                    attributes = {
                        "AppliedValue": value_data["appliedValue"],
                        "Category": value_data["costCategory"],
                    }
                elif value_data["costType"] == "SUM":
                    attributes = {"Category": "*"}
                if value_data["unitBasisValue"]:
                    attributes["UnitBasis"] = {
                        "ValueComponent": value_data["unitBasisValue"],
                        "UnitComponent": ifc_file.by_id(value_data["unitComponent"]),
                    }
                ifcopenshell.api.cost.edit_cost_value(file=ifc_file, cost_value=value, attributes=attributes)
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "addProductAssignments":
            prop_name = operator_data["propName"]
            if prop_name == "count":
                prop_name = ""
            bonsai.core.cost.assign_cost_item_quantity(
                tool.Ifc,
                tool.Cost,
                cost_item=ifc_file.by_id(operator_data["costItemId"]),
                related_object_type="PRODUCT",
                prop_name=prop_name,
            )
            cost_schedule = tool.Cost.get_cost_schedule(cost_item=tool.Ifc.get().by_id(operator_data["costItemId"]))
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "enableEditingQuantities":
            cost_item_id = operator_data["costItemId"]
            cost_item = ifc_file.by_id(cost_item_id)
            cls.load_cost_item_quantities_ui(cost_item)
        if operator_data["type"] == "AddCostItemQuantity":
            cost_item_id = operator_data["costItemId"]
            cost_item = ifc_file.by_id(cost_item_id)
            cost_schedule = tool.Cost.get_cost_schedule(cost_item)
            tool.Ifc.run("cost.add_cost_item_quantity", cost_item=cost_item, ifc_class=operator_data["ifcClass"])
            cls.load_cost_schedule_web_ui(cost_schedule)
            cls.load_cost_item_quantities_ui(cost_item)
        if operator_data["type"] == "editCostItemQuantity":
            cost_item_id = operator_data["costItemId"]
            cost_item = ifc_file.by_id(cost_item_id)
            cost_schedule = tool.Cost.get_cost_schedule(cost_item)
            physical_quantity = tool.Ifc.get().by_id(operator_data["quantityId"])
            tool.Ifc.run(
                "cost.edit_cost_item_quantity",
                physical_quantity=physical_quantity,
                attributes=operator_data["attributes"],
            )
            cls.load_cost_schedule_web_ui(cost_schedule)
            cls.load_cost_item_quantities_ui(cost_item)
        if operator_data["type"] == "deleteCostItemQuantity":
            cost_item = ifc_file.by_id(operator_data["costItemId"])
            physical_quantity = ifc_file.by_id(operator_data["quantityId"])
            tool.Ifc.run("cost.remove_cost_item_quantity", cost_item=cost_item, physical_quantity=physical_quantity)
            cost_schedule = tool.Cost.get_cost_schedule(cost_item)
            cls.load_cost_schedule_web_ui(cost_schedule)
            cls.load_cost_item_quantities_ui(cost_item)
        if operator_data["type"] == "enableEditingClassification":
            cost_item = ifc_file.by_id(operator_data["costItemId"])
            cost_classifications = []
            for reference in get_references(cost_item):
                cost_classification_data = reference.get_info()
                del cost_classification_data["ReferencedSource"]
                cost_classifications.append(cost_classification_data)
            classification_data, classification_name = get_classification_data(IfcStore.classification_file)
            data = {
                "classification_data": classification_data,
                "classification_name": classification_name,
                "cost_item_id": cost_item.id(),
                "cost_classifications": cost_classifications,
            }
            cls.send_webui_data(
                data=data,
                data_key="classification",
                event="classification",
            )
        if operator_data["type"] == "removeClassificationReference":
            cost_item = ifc_file.by_id(operator_data["costItemId"])
            cost_schedule = tool.Cost.get_cost_schedule(cost_item)
            reference = ifc_file.by_id(operator_data["classificationId"])
            tool.Ifc.run("classification.remove_reference", products=[cost_item], reference=reference)
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "addClassificationReference":
            cost_item = ifc_file.by_id(operator_data["costItemId"])
            cost_schedule = tool.Cost.get_cost_schedule(cost_item)
            classification = None
            classification_name = operator_data["classificationName"]
            for element in tool.Ifc.get().by_type("IfcClassification"):
                if element.Name == classification_name:
                    classification = element
                    break
            reference = IfcStore.classification_file.by_id(operator_data["classificationId"])
            tool.Ifc.run(
                "classification.add_reference", products=[cost_item], reference=reference, classification=classification
            )
            cls.load_cost_schedule_web_ui(cost_schedule)
        if operator_data["type"] == "assignFromQuery":
            prop_name = operator_data["propName"]
            cost_item = ifc_file.by_id(operator_data["costItemId"])
            results = []
            try:
                results = filter_elements(ifc_file, operator_data["query"])
            except Exception as e:
                cls.send_webui_data(
                    data={
                        "error": "Your query is invalid. Please check the syntax and try again.",
                        "container": "query-quantities-section-" + str(operator_data["costItemId"]),
                    },
                    data_key="message",
                    event="message",
                )
                return
            if not results:
                cls.send_webui_data(
                    data={
                        "error": "No elements found with the specified query. Are you sure the query is correct?",
                        "container": "query-quantities-section-" + str(operator_data["costItemId"]),
                    },
                    data_key="message",
                    event="message",
                )
                return
            products_with_quantity = [r for r in results if has_property(r, prop_name)]
            if products_with_quantity:
                tool.Ifc.run(
                    "cost.assign_cost_item_quantity",
                    cost_item=cost_item,
                    products=results,
                    prop_name=prop_name,
                )
                cost_schedule = tool.Cost.get_cost_schedule(cost_item)
                cls.load_cost_schedule_web_ui(cost_schedule)
                cls.send_webui_data(
                    data={
                        "success": f"Successfully assigned quantity from {len(products_with_quantity)} products.",
                        "container": "query-quantities-section-" + str(operator_data["costItemId"]),
                    },
                    data_key="message",
                    event="message",
                )
            else:
                cls.send_webui_data(
                    data={
                        "error": f"Found {len(results)} products, but none with the specified property '{prop_name}'.",
                        "container": "query-quantities-section-" + str(operator_data["costItemId"]),
                    },
                    data_key="message",
                    event="message",
                )
        if operator_data["type"] == "assignCostValues":
            cost_rate = ifc_file.by_id(operator_data["costRateId"])
            cost_schedule = tool.Cost.get_cost_schedule(ifc_file.by_id(operator_data["costItemIds"][0]))
            for cost_item_id in operator_data["costItemIds"]:
                cost_item = ifc_file.by_id(cost_item_id)
                tool.Ifc.run("cost.assign_cost_value", cost_item=cost_item, cost_rate=cost_rate)
            cls.load_cost_schedule_web_ui(cost_schedule)

    @classmethod
    def load_cost_item_quantities_ui(cls, cost_item: ifcopenshell.entity_instance) -> None:
        if not cost_item:
            return
        selected_products = list(tool.Spatial.get_selected_products())
        selected_products_data = cls.selection_data(cost_item, selected_products)

        assigned_products = tool.Cost.get_cost_item_products(cost_item, is_deep=False)
        assigned_products_data = cls.selection_data(cost_item, assigned_products)

        names = ifcopenshell.util.cost.get_product_quantity_names(selected_products)
        cls.send_webui_data(
            data={
                "selected_products": selected_products_data,
                "assigned_products": assigned_products_data,
                "product_quantity_names": names,
                "cost_item_id": cost_item.id(),
                "cost_quantities": tool.Cost.get_cost_quantities(cost_item),
            },
            data_key="quantities",
            event="quantities",
        )

    @classmethod
    def selection_data(cls, cost_item: ifcopenshell.entity_instance, elements: list) -> list:
        if not elements:
            return []
        if not cost_item:
            return [
                {
                    "info": {
                        "id": element.id(),
                        "name": element.Name,
                        "class": element.is_a(),
                        "type": get_type(element).Name if get_type(element) else None,
                    },
                    "qtos": get_psets(element, qtos_only=True),
                }
                for element in elements or []
            ]
        data = []
        for element in elements or []:
            psets = get_psets(element, qtos_only=True)
            element_type = get_type(element)
            quantities, unit = tool.Cost.get_assigned_quantities(cost_item, element)
            data.append(
                {
                    "info": {
                        "id": element.id(),
                        "name": element.Name,
                        "class": element.is_a(),
                        "type": element_type.Name if element_type else None,
                    },
                    "qtos": psets,
                    "assigned_quantities": [
                        {
                            "cost_item_id": cost_item.id(),
                            "product_id": element.id(),
                            "name": q.Name,
                            "value": q[3],
                            "type": q.Unit,
                        }
                        for q in quantities or []
                    ],
                    "unit": unit,
                }
            )
        return data

    @classmethod
    def load_cost_schedule_web_ui(cls, cost_schedule: ifcopenshell.entity_instance) -> None:
        ifc2json = ifc5D2json()
        ifc2json.file_path = tool.Ifc.get()
        ifc2json.cost_schedule = cost_schedule
        schedule_data = ifc2json.convert_ifc_to_json()
        cls.send_webui_data(
            data={
                "currency": tool.Cost.currency(),
                "schedule_data": schedule_data,
            },
            data_key="cost_items",
            event="cost_items",
        )

    @classmethod
    def handle_gantt_operator(cls, operator_data: dict) -> None:
        """
        this method handles the Sequencing page operators.

        Args:
            operator_data (dict): A dictionary containing the operator data.
        """
        ifc_file = tool.Ifc.get()
        if operator_data["type"] == "getWorkSchedules":
            work_schedules = ifc_file.by_type("IfcWorkSchedule")
            work_schedules_json = [ws.get_info(recursive=True) for ws in work_schedules]
            cls.send_webui_data(data=work_schedules_json, data_key="work_schedule_info", event="work_schedule_info")
        if operator_data["type"] == "loadWorkSchedule":
            work_schedule = ifc_file.by_id(operator_data["workScheduleId"])
            print("Generating Gantt chart")
            bonsai.core.sequence.enable_editing_work_schedule_tasks(tool.Sequence, work_schedule=work_schedule)
            bonsai.core.sequence.generate_gantt_chart(tool.Sequence, work_schedule=work_schedule)
        if operator_data["type"] == "editTask":
            task_id = int(operator_data["taskId"])
            task = ifc_file.by_id(task_id)
            task_time = task.TaskTime
            column = operator_data["column"]
            new_value = operator_data["value"]
            if task_time is None:
                ifcopenshell.api.sequence.add_task_time(ifc_file, task)
                task_time = task.TaskTime
            ifcopenshell.api.sequence.edit_task_time(
                ifc_file, task_time=task_time, attributes={IFC_TASK_ATTRIBUTE_MAP[column]: str(new_value)}
            )

            bpy.ops.bim.load_task_properties()
            # after updating, send new gantt data to handle the case where
            # changing a task cascades and changes other tasks. as this wouldn't
            # be reflected in the web ui
            work_schedule = ifc_file.by_id(operator_data["workScheduleId"])
            task_json = tool.Sequence.create_tasks_json(work_schedule)
            gantt_data = {"tasks": task_json, "work_schedule": work_schedule.get_info(recursive=True)}
            cls.send_webui_data(data=gantt_data, data_key="gantt_data", event="gantt_data")

    @classmethod
    def handle_drawings_operator(cls, operator_data: dict) -> None:
        """
        this method handles the Documentation page operators.

        Args:
            operator_data (dict): A dictionary containing the operator data.
        """
        if operator_data["type"] == "getDrawings":
            drawings_data = []
            sheets_data = []
            ifc_file_dir = os.path.dirname(bpy.context.scene.BIMProperties.ifc_file)

            sheets = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"]
            for sheet in sorted(sheets, key=lambda s: getattr(s, "Identification", getattr(s, "DocumentId", None))):
                for reference in tool.Drawing.get_document_references(sheet):
                    reference_description = tool.Drawing.get_reference_description(reference)
                    if reference_description != "SHEET":
                        continue
                    reference_name = os.path.basename(reference.Location)
                    reference_path = os.path.join(ifc_file_dir, reference.Location)
                    reference_path = os.path.normpath(reference_path)
                    sheets_data.append({"name": reference_name, "path": reference_path})

            drawings = [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
            for drawing in drawings:
                document = tool.Drawing.get_drawing_document(drawing)
                reference_name = os.path.basename(document.Location)
                reference_path = os.path.join(ifc_file_dir, document.Location)
                reference_path = os.path.normpath(reference_path)
                drawings_data.append({"name": reference_name, "path": reference_path})

            cls.send_webui_data(
                data={"drawings": drawings_data, "sheets": sheets_data}, data_key="drawings_data", event="drawings_data"
            )

    @classmethod
    def open_web_browser(cls, port: int, page: str = "") -> None:
        """
        Opens a web browser and navigates to the specified URL.

        Args:
            port (int): The port number to be used in the URL.
            page (str): The page name to be appended to the URL. Default is an empty string which points to the index page.
        """
        webbrowser.open(f"http://127.0.0.1:{port}/{page}")

    @classmethod
    def send_theme_data(cls) -> None:
        """
        this method retrieves the theme colors from Blender preferences,
        calculates the mixed colors, and sends the theme data to the Web UI.
        """

        def get_color(theme, attribute) -> tuple[Any, ...]:
            return tuple(getattr(theme, attribute)[:])

        def mix_colors(color1, color2):
            alpha1 = color1[3] * 255 if len(color1) > 3 else 255
            alpha2 = color2[3] * 255 if len(color2) > 3 else 255

            alpha = 255 - ((255 - alpha1) * (255 - alpha2) / 255)
            red = (color1[0] * (255 - alpha2) + color2[0] * alpha2) / 255
            green = (color1[1] * (255 - alpha2) + color2[1] * alpha2) / 255
            blue = (color1[2] * (255 - alpha2) + color2[2] * alpha2) / 255
            return red, green, blue, alpha / 255

        prefs = bpy.context.preferences.themes[0].preferences.space
        panel = prefs.panelcolors
        view_3d = bpy.context.preferences.themes[0].view_3d
        top_bar = bpy.context.preferences.themes[0].topbar.space
        info = bpy.context.preferences.themes[0].info
        outliner = bpy.context.preferences.themes[0].outliner
        ui = bpy.context.preferences.themes[0].user_interface

        theme = {
            "window_background": get_color(prefs, "back"),
            "text": get_color(prefs, "text"),
            "tab_background": get_color(prefs, "tab_back"),
            "tab_outline": get_color(prefs, "tab_outline"),
            "panel_header": get_color(panel, "header"),
            "panel_background": mix_colors(get_color(panel, "back"), get_color(panel, "sub_back")),
            "top_bar_header": get_color(top_bar, "header"),
            "top_bar_header_text": get_color(top_bar, "header_text"),
            "active_object": get_color(view_3d, "object_active"),
            "selected_object": get_color(view_3d, "object_selected"),
            "info_warning": get_color(info, "info_warning_text"),
            "odd_row": get_color(outliner.space, "back"),
            "even_row": mix_colors(get_color(outliner.space, "back"), get_color(outliner, "row_alternate")),
            "active_highlight": get_color(outliner, "active"),
            "active_text_highlight": get_color(outliner, "active_object"),
            "button_background": get_color(ui.wcol_tool, "inner"),
            "button_test": get_color(ui.wcol_tool, "text"),
            "button_border": get_color(ui.wcol_tool, "outline"),
        }
        cls.send_webui_data(theme, "theme", "theme_data", use_web_data=False)

    @classmethod
    async def sio_connect(cls, url: str) -> None:
        """
        Asynchronously establishes a WebSocket connection and sets up event listeners.

        This method connects to the specified URL using WebSocket transport and registers
        an event listener for the `web_operator` event within the `/blender` namespace.

        Args:
            url (str): The URL of the WebSocket server to connect to.
        """
        await sio.connect(url, transports=["websocket"], namespaces="/blender")
        sio.on("web_operator", cls.sio_listen_web_operator, namespace="/blender")

    @classmethod
    async def sio_disconnect(cls) -> None:
        """
        Asynchronously disconnects the WebSocket connection.

        This method terminates the active WebSocket connection established by the `sio_connect` method.
        """
        await sio.disconnect()

    @classmethod
    async def sio_send(cls, data: Any, event: str = "data", namespace: str = "/blender") -> None:
        """
        Asynchronously sends data to the WebSocket server.

        This method emits an event with the provided data to the WebSocket server within the specified namespace.

        Args:
            data (Any): The data to send to the WebSocket server.
            event (Optional[str]): The WebSocket event to emit. Defaults to "data".
            namespace (Optional[str]): The namespace for the WebSocket event. Defaults to "/blender".
        """
        await sio.emit(event, data, namespace=namespace)

    @classmethod
    async def sio_listen_web_operator(cls, data: dict) -> None:
        """
        Asynchronously handles incoming `web_operator` events from the WebSocket server.

        This method receives data from the WebSocket server and attempts to place it into the
        `web_operator_queue`. If the queue is full, the data is discarded.

        Args:
            data (dict): The data received from the `web_operator` event.
        """
        try:
            web_operator_queue.put_nowait(data)
        except queue.Full:
            pass

    @classmethod
    def set_is_running(cls, is_running: bool) -> None:
        bpy.context.scene.WebProperties.is_running = is_running

    @classmethod
    def set_is_connected(cls, is_connected: bool) -> None:
        bpy.context.scene.WebProperties.is_connected = is_connected


class AsyncioThread(threading.Thread):
    def __init__(self, *args, loop=None, **kwargs):
        """
        Initialize an instance of AsyncioThread.

        This class represents a thread that runs an asyncio event loop. It is used to handle asynchronous tasks
        in a separate thread from the main thread.

        Args:
           *args: Variable length argument list. These arguments are passed to the superclass constructor.
           loop: An existing asyncio event loop. If None, a new event loop is created.
           **kwargs: Arbitrary keyword arguments. These arguments are passed to the superclass constructor.
        """
        super().__init__(*args, **kwargs)
        self.loop = loop or asyncio.new_event_loop()
        self.running = False

    def run(self):
        """
        Start the asyncio event loop and mark the thread as running.
        """
        self.running = True
        self.loop.run_forever()

    def run_coro(self, coro) -> Any:
        """
        Run a coroutine in the asyncio event loop from a separate thread.

        Args:
           coro: The coroutine to be run.

        Returns:
            The result of the coroutine.
        """
        return asyncio.run_coroutine_threadsafe(coro, loop=self.loop).result()

    def stop(self) -> None:
        """
        Stop the asyncio event loop and join the thread.
        """
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
        self.running = False
