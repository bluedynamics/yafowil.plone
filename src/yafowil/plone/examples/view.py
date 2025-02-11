# -*- coding: utf-8 -*-
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five import BrowserView
from yafowil.base import factory
from yafowil.controller import Controller
from yafowil.utils import get_example
from yafowil.utils import get_example_names
from zExceptions import NotFound

import yafowil.loader  # noqa  # loads registry


class ExampleResponseView(BrowserView):
    def __call__(self):
        route = self.route(self.request["URL"])
        for header in route.get("header", []):
            self.request.response.setHeader(*header)
        return route.get("body", "")


class ExampleView(BrowserView):
    def __init__(self, context, request):
        super(ExampleView, self).__init__(context, request)
        add_bundle_on_request(request, "yafowil")

    @property
    def example_names(self):
        return sorted(get_example_names())

    @property
    def example(self):
        if self.example_name:
            return get_example(self.example_name)

    @property
    def example_name(self):
        if hasattr(self, "_example_name"):
            return self._example_name

    @property
    def route(self):
        if hasattr(self, "_route"):
            return self._route

    def forms(self):
        result = list()
        for part in self.example:
            widget = part["widget"]
            form = factory(
                "form",
                name="form-%s" % widget.name,
                props={"action": self.example_name},
            )
            form[widget.name] = widget
            form["submit"] = factory(
                "submit",
                props={
                    "label": "submit",
                    "action": "save",
                    "handler": lambda widget, data: None,
                },
            )
            controller = Controller(form, self.request)
            result.append(controller.rendered)
        return result

    def publishTraverse(self, request, name):
        if self.example_name:
            view = ExampleResponseView(self.context, self.request)
            view.routes = dict()
            for part in self.example:
                routes = part.get("routes", [])
                if name in routes:
                    view.route = routes[name]
                    return view
            raise NotFound()
        if name not in self.example_names:
            raise NotFound()
        self._example_name = name
        return self
